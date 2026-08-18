"""Lokale, transparente Systemdatei-Mischquelle für PW-Tool.

Die Funktionen in diesem Modul lesen ausschließlich eine feste Allowlist
nicht-sensibler Betriebssystemdateien. Sie durchsuchen niemals das Dateisystem,
lesen keine Nutzerprofile und übertragen oder speichern keine Daten.

Öffentliche Systemdateien sind kein Geheimnis. Ihre Hashwerte sind daher nur
optionales Zusatzmaterial; die primäre Entropie bleibt immer ``secrets`` bzw.
die zugrunde liegende OS-Zufallsquelle.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import os
from pathlib import Path
import platform
import sys
from typing import Iterable, Optional, Sequence, Tuple


MAXIMUM_SOURCES = 5
MINIMUM_SOURCES = 3
MAXIMUM_BYTES_PER_SOURCE = 8 * 1024 * 1024
BUFFER_SIZE = 64 * 1024
AGGREGATE_DOMAIN = b"PW-Tool SystemFileDigest v1"
MIX_DOMAIN = b"PW-Tool SystemMix v1"


class SystemMixStatus(str, Enum):
    """Öffentlich darstellbarer Zustand der optionalen Zusatzquelle."""

    DISABLED = "disabled"
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class SystemMixResult:
    """Ergebnis ohne Preisgabe von Pfaden, Namen oder einzelnen Hashwerten."""

    status: SystemMixStatus
    source_count: int
    aggregate_digest: Optional[bytes] = None

    @classmethod
    def disabled(cls) -> "SystemMixResult":
        return cls(SystemMixStatus.DISABLED, 0, None)

    @classmethod
    def unavailable(cls) -> "SystemMixResult":
        return cls(SystemMixStatus.UNAVAILABLE, 0, None)


@dataclass(frozen=True)
class _DigestEntry:
    stable_id: str
    bytes_read: int
    digest: bytes


def detect_platform() -> str:
    """Erkennt die unterstützte Laufzeitplattform ohne Geräteidentifikatoren."""
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("win"):
        return "windows"
    if _is_android():
        return "android"
    if sys.platform.startswith("linux"):
        return "linux"
    return "unsupported"


def _is_android() -> bool:
    """Erkennt typische Python-Laufzeiten auf Android, etwa Termux."""
    return bool(
        os.environ.get("ANDROID_ROOT")
        or os.environ.get("ANDROID_DATA")
        or os.environ.get("TERMUX_VERSION")
        or "android" in platform.release().lower()
    )


def candidate_paths(platform_id: Optional[str] = None) -> Tuple[Tuple[str, Path], ...]:
    """Gibt ausschließlich die dokumentierte, feste Plattform-Allowlist zurück."""
    platform_id = platform_id or detect_platform()

    if platform_id == "macos":
        return (
            ("macos-system-version", Path("/System/Library/CoreServices/SystemVersion.plist")),
            ("macos-zone-tab", Path("/usr/share/zoneinfo/zone.tab")),
            ("macos-zone-utc", Path("/usr/share/zoneinfo/UTC")),
            ("macos-core-foundation", Path("/System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation")),
            ("macos-hosts", Path("/etc/hosts")),
        )

    if platform_id == "windows":
        windows_root = Path(os.environ.get("WINDIR", r"C:\Windows"))
        return (
            ("windows-kernel32", windows_root / "System32" / "kernel32.dll"),
            ("windows-ntdll", windows_root / "System32" / "ntdll.dll"),
            ("windows-advapi32", windows_root / "System32" / "advapi32.dll"),
            ("windows-hosts", windows_root / "System32" / "drivers" / "etc" / "hosts"),
            ("windows-winini", windows_root / "win.ini"),
        )

    if platform_id == "android":
        return (
            ("android-system-build-prop", Path("/system/build.prop")),
            ("android-system-hosts", Path("/system/etc/hosts")),
            ("android-system-ld-config", Path("/system/etc/ld.config.txt")),
            ("android-runtime-libraries", Path("/apex/com.android.runtime/etc/public.libraries.txt")),
            ("android-vendor-build-prop", Path("/vendor/build.prop")),
        )

    if platform_id == "linux":
        return (
            ("linux-os-release", Path("/etc/os-release")),
            ("linux-proc-version", Path("/proc/version")),
            ("linux-zone-tab", Path("/usr/share/zoneinfo/zone.tab")),
            ("linux-zone-utc", Path("/usr/share/zoneinfo/UTC")),
            ("linux-hosts", Path("/etc/hosts")),
        )

    return ()


def collect_system_mix(
    *,
    enabled: bool = True,
    platform_id: Optional[str] = None,
    candidates: Optional[Sequence[Tuple[str, Path]]] = None,
    maximum_bytes_per_source: int = MAXIMUM_BYTES_PER_SOURCE,
) -> SystemMixResult:
    """Hasht bis zu fünf feste, lesbare Quellen in konstanten Puffern.

    Bei weniger als drei Quellen wird absichtlich kein Digest zurückgegeben.
    Der aufrufende Generator verwendet dann weiterhin ausschließlich sicheren
    Systemzufall und kann den Fallback transparent anzeigen.
    """
    if not enabled:
        return SystemMixResult.disabled()
    if maximum_bytes_per_source <= 0:
        raise ValueError("maximum_bytes_per_source must be positive")

    resolved_platform = platform_id or detect_platform()
    resolved_candidates = candidates if candidates is not None else candidate_paths(resolved_platform)
    entries = []

    for stable_id, path in resolved_candidates:
        if len(entries) >= MAXIMUM_SOURCES:
            break
        entry = _digest_path(stable_id, path, maximum_bytes_per_source)
        if entry is not None:
            entries.append(entry)

    if len(entries) >= MINIMUM_SOURCES:
        return SystemMixResult(
            status=SystemMixStatus.COMPLETE,
            source_count=len(entries),
            aggregate_digest=_aggregate_entries(resolved_platform, entries),
        )
    if entries:
        return SystemMixResult(SystemMixStatus.PARTIAL, len(entries), None)
    return SystemMixResult.unavailable()


def mix_entropy(system_random: bytes, system_mix: SystemMixResult) -> bytes:
    """Kombiniert Entropie sicher mit einem vollständigen Dateidigest.

    Es wird bewusst HMAC-SHA-512 statt einer Bit- oder Integer-Multiplikation
    verwendet. Bei nicht vollständigem Mix wird ``system_random`` unverändert
    kopiert zurückgegeben.
    """
    if not system_random:
        raise ValueError("system_random must not be empty")

    if system_mix.status is not SystemMixStatus.COMPLETE or system_mix.aggregate_digest is None:
        return bytes(system_random)

    digest = system_mix.aggregate_digest
    if len(digest) != hashlib.sha512().digest_size:
        raise ValueError("aggregate digest must be a SHA-512 digest")

    message = MIX_DOMAIN + _length_prefix(digest)
    return hmac.new(system_random, message, hashlib.sha512).digest()


def _digest_path(
    stable_id: str,
    path: Path,
    maximum_bytes: int,
) -> Optional[_DigestEntry]:
    """Liest eine einzelne Allowlist-Datei; Fehler bleiben absichtlich stumm."""
    try:
        if not path.is_file():
            return None
        digest = hashlib.sha512()
        total_bytes = 0
        with path.open("rb") as source:
            while total_bytes < maximum_bytes:
                remaining = min(BUFFER_SIZE, maximum_bytes - total_bytes)
                block = source.read(remaining)
                if not block:
                    break
                digest.update(block)
                total_bytes += len(block)
        if total_bytes == 0:
            return None
        return _DigestEntry(stable_id, total_bytes, digest.digest())
    except (OSError, PermissionError):
        return None


def _aggregate_entries(platform_id: str, entries: Iterable[_DigestEntry]) -> bytes:
    """Bildet einen eindeutigen, geordneten und versionierten Gesamtdigest."""
    entry_list = tuple(entries)
    aggregate = hashlib.sha512()
    aggregate.update(AGGREGATE_DOMAIN)
    aggregate.update(_length_prefix(platform_id.encode("utf-8")))
    aggregate.update(len(entry_list).to_bytes(4, "big"))

    for entry in entry_list:
        aggregate.update(_length_prefix(entry.stable_id.encode("utf-8")))
        aggregate.update(entry.bytes_read.to_bytes(8, "big"))
        aggregate.update(_length_prefix(entry.digest))

    return aggregate.digest()


def _length_prefix(value: bytes) -> bytes:
    return len(value).to_bytes(4, "big") + value

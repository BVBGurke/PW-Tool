"""Sichere, rein lokale Demonstration einer gesalzenen Passwort-KDF.

Das Modul ist kein Crack-Werkzeug: Es akzeptiert keine fremden Hashes oder
Kandidatenlisten. Jeder Aufruf erzeugt einen frischen lokalen Demo-Wert, leitet
ihm einmal mit scrypt ab und prüft ausschließlich diesen selben Prozesswert.
Klartext, Salt und abgeleitete Bytes verlassen die Funktion nicht.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import os
import platform
from time import perf_counter

from cuda_engine import get_cuda_engine
from password_engine import CharacterSet, PasswordGenerator


SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 32
SCRYPT_SALT_LENGTH = 16
SCRYPT_MAXMEM = 64 * 1024 * 1024


@dataclass(frozen=True)
class LocalHashDemoReport:
    """Nicht sensitive Metadaten des einmaligen lokalen KDF-Durchlaufs."""

    algorithm: str
    n: int
    r: int
    p: int
    salt_length: int
    derived_key_length: int
    duration_ms: float
    self_verification_passed: bool
    execution_path: str
    accelerator_status: str

    def as_text(self) -> str:
        """Rendert ausschließlich öffentliche Parameter und kein Geheimnis."""
        verification = "erfolgreich" if self.self_verification_passed else "fehlgeschlagen"
        return "\n".join(
            (
                "Hash-Demo (nur lokal, kein Crack-Versuch)",
                f"KDF: {self.algorithm}; N={self.n}, r={self.r}, p={self.p}",
                f"Salt: {self.salt_length} Byte; abgeleiteter Wert: {self.derived_key_length} Byte",
                f"Einmalige Selbstverifikation: {verification}",
                f"KDF-Dauer: {self.duration_ms:.1f} ms",
                f"Ausführung: {self.execution_path}",
                f"Beschleunigerstatus: {self.accelerator_status}",
                "Klartext, Salt und Hash werden nicht angezeigt, gespeichert oder geloggt.",
            )
        )


def _derive(password: str, salt: bytes) -> bytes:
    """Führt die fest begrenzte scrypt-Ableitung für die Demo aus."""
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        maxmem=SCRYPT_MAXMEM,
        dklen=SCRYPT_DKLEN,
    )


def _accelerator_status() -> str:
    """Beschreibt nur die sichere CPU-Fallback-Entscheidung.

    Eine erkannte GPU bleibt Statusinformation. Die Demo übergibt niemals
    Passwortmaterial an CUDA, bis ein separat auditierter KDF-Pfad vorliegt.
    """
    cuda_engine = get_cuda_engine()
    if cuda_engine.available:
        return "CUDA erkannt; für die Hash-Demo bewusst nicht verwendet"
    if os.environ.get("TERMUX_VERSION") or os.environ.get("ANDROID_ROOT"):
        return "Android/Termux erkannt; sicherer CPU-Fallback aktiv"
    return f"Keine auditierte CUDA-KDF verfügbar; CPU-Fallback auf {platform.system()}"


def run_local_hash_demo(length: int, charset: CharacterSet) -> LocalHashDemoReport:
    """Demonstriert eine sichere Passwortspeicherung nur mit frischem Demo-Wert.

    Es gibt bewusst keinen Parameter für gespeicherte Hashes, Passwörter,
    Wortlisten oder Angriffsstrategien. Damit bleibt die Funktion auf eine
    kontrollierte, lokale Einmal-Demonstration begrenzt.
    """
    demo_password = PasswordGenerator.generate_policy(length, charset)
    salt = os.urandom(SCRYPT_SALT_LENGTH)

    start = perf_counter()
    derived = _derive(demo_password, salt)
    duration_ms = (perf_counter() - start) * 1000
    verified = hmac.compare_digest(_derive(demo_password, salt), derived)

    return LocalHashDemoReport(
        algorithm="scrypt",
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        salt_length=SCRYPT_SALT_LENGTH,
        derived_key_length=SCRYPT_DKLEN,
        duration_ms=duration_ms,
        self_verification_passed=verified,
        execution_path="CPU-scrypt mit frischem OS-CSPRNG-Salt",
        accelerator_status=_accelerator_status(),
    )

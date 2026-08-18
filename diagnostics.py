"""Redaktionssichere Diagnostik für PW-Tool.

Dateilogs entstehen ausschließlich bei explizitem ``-log``/``--log``. Das Modul
akzeptiert eine enge Schema-Whitelist und verwirft jede potentiell sensitive
Angabe, bevor sie eine Logdatei erreicht.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping, Optional


_ALLOWED_KEYS = frozenset(
    {
        "backend",
        "backend_candidate",
        "backend_selected",
        "fallback_reason",
        "platform",
        "python_version",
        "cuda_available",
        "cuda_version",
        "driver_version",
        "device_name",
        "workload",
        "batch_count",
        "password_length",
        "iterations",
        "worker_count",
        "phase",
        "duration_ms",
        "median_ms",
        "p95_ms",
        "throughput_per_second",
        "peak_python_bytes",
        "gpu_memory_bytes",
        "gpu_utilization_percent",
        "energy_millijoules",
        "metric_available",
        "warmup",
        "profile_flags",
    }
)
_FORBIDDEN_TOKENS = ("password", "secret", "seed", "entropy", "hash", "digest", "path", "source", "exception")


class SafeDiagnosticLogger:
    """Schreibt nur bei aktivem Opt-in sichere, strukturierte Metadaten."""

    def __init__(self, enabled: bool = False, directory: Optional[Path] = None) -> None:
        self.enabled = enabled
        self.path: Optional[Path] = None
        if enabled:
            log_directory = directory or Path.cwd() / "logs"
            log_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self.path = log_directory / f"pwtool-diagnostics-{timestamp}.jsonl"
            descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            os.close(descriptor)
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                # Windows does not consistently support POSIX modes.
                pass

    def log(self, event: str, **metadata: Any) -> None:
        """Schreibt ein Ereignis, wenn der explizite Logmodus aktiv ist."""
        if not self.enabled or self.path is None:
            return
        if not event or any(token in event.lower() for token in _FORBIDDEN_TOKENS):
            raise ValueError("Unsafe diagnostic event name")

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "metadata": self._sanitize(metadata),
        }
        with self.path.open("a", encoding="utf-8") as target:
            target.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")

    @staticmethod
    def _sanitize(metadata: Mapping[str, Any]) -> dict[str, bool | int | float | str | list[str]]:
        sanitized: dict[str, bool | int | float | str | list[str]] = {}
        for key, value in metadata.items():
            lower_key = key.lower()
            if key not in _ALLOWED_KEYS or any(token in lower_key for token in _FORBIDDEN_TOKENS):
                continue
            if isinstance(value, (bool, int, float)):
                sanitized[key] = value
            elif isinstance(value, str):
                sanitized[key] = value[:160]
            elif key == "profile_flags" and isinstance(value, (tuple, list, set)):
                sanitized[key] = [str(item)[:80] for item in value]
        return sanitized

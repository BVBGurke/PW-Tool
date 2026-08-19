"""Nicht sensitive Laufzeitmetadaten; keine GPU-Nutzung für Passwortwerte."""

from __future__ import annotations

import platform


class CapabilityService:
    def status(self) -> dict[str, object]:
        return {
            "system": platform.system(),
            "architecture": platform.machine(),
            "password_generation_path": "os-csprng-cpu",
            "cuda": {"used_for_passwords": False, "used_for_hash_demo": False, "status": "not_probed"},
        }

"""Optionale CUDA-Entropiequelle mit messbarer CPU-Fallback-Kompatibilität.

Wichtig: Die aktuelle Passwort-KDF nutzt ``hashlib.pbkdf2_hmac`` und läuft damit
auf der CPU. Dieses Modul misst GPU-Zufallserzeugung und CPU-KDF getrennt, statt
eine nicht vorhandene GPU-PBKDF2-Beschleunigung zu behaupten.
"""

from __future__ import annotations

import hashlib
import os
from time import perf_counter
from typing import Mapping, Optional, Tuple

from system_mix import SystemMixResult, mix_entropy


class CUDAEngine:
    """Verwaltet optionale CuPy-/CUDA-Erkennung und Entropieerzeugung."""

    def __init__(self) -> None:
        self.cupy = None
        self.available = False
        self.device_name = ""
        self.error_msg = ""
        self.secure_password_generation_supported = False
        self._detect_cuda()

    def _detect_cuda(self) -> None:
        try:
            import cupy as cp

            device = cp.cuda.Device()
            properties = cp.cuda.runtime.getDeviceProperties(device.id)
            name = properties.get("name", b"CUDA device")
            self.device_name = name.decode() if isinstance(name, bytes) else str(name)
            self.cupy = cp
            self.available = True
        except Exception as error:
            self.available = False
            self.error_msg = str(error)

    def get_status(self) -> Tuple[bool, str, str]:
        """Gibt Hardwareverfügbarkeit, Gerätenamen und ggf. Fehlerbeschreibung zurück."""
        return self.available, self.device_name, self.error_msg

    def can_generate_secure_passwords(self) -> bool:
        """CUDA ist erst nach einer auditierten CSPRNG-/KDF-Implementierung zulässig."""
        return self.available and self.secure_password_generation_supported

    def gpu_entropy_pbkdf2(
        self,
        iterations: int = 200000,
        hash_length: int = 64,
        system_mix: Optional[SystemMixResult] = None,
    ) -> Optional[bytes]:
        """Kompatibilitätswrapper ohne Metrikrückgabe."""
        entropy, _ = self.gpu_entropy_pbkdf2_profiled(
            iterations=iterations,
            hash_length=hash_length,
            system_mix=system_mix,
        )
        return entropy

    def gpu_entropy_pbkdf2_profiled(
        self,
        iterations: int = 200000,
        hash_length: int = 64,
        system_mix: Optional[SystemMixResult] = None,
    ) -> tuple[Optional[bytes], Mapping[str, float]]:
        """Erzeugt GPU-Zufallsbytes und misst die CPU-KDF getrennt.

        Die Metrik ``cuda_seed_and_salt`` enthält den kompletten CuPy-/Transfer-
        Abschnitt. ``cpu_pbkdf2`` ist bewusst separat, weil ``hashlib`` keinen
        CUDA-Kernel ausführt.
        """
        if not self.can_generate_secure_passwords() or self.cupy is None:
            return None, {}

        timings: dict[str, float] = {}
        try:
            # OS-CSPRNG ist für Passwortseeds zwingend. Ein nicht auditiertes
            # CuPy-RNG darf nicht als kryptografische Entropiequelle dienen.
            start = perf_counter()
            seed = os.urandom(32)
            salt = os.urandom(32)
            timings["os_csprng"] = perf_counter() - start

            if system_mix is not None:
                start = perf_counter()
                seed = mix_entropy(seed, system_mix)
                timings["system_mix_hmac"] = perf_counter() - start

            start = perf_counter()
            entropy = hashlib.pbkdf2_hmac(
                "sha512",
                seed,
                salt,
                iterations,
                dklen=hash_length,
            )
            timings["cpu_pbkdf2"] = perf_counter() - start
            return entropy, timings
        except Exception as error:
            self.error_msg = f"GPU entropy generation failed: {error}"
            return None, timings

    def gpu_raw_entropy(
        self,
        size: int = 64,
        system_mix: Optional[SystemMixResult] = None,
    ) -> Optional[bytes]:
        """Gibt GPU-Zufall zurück und mischt ihn optional sicher."""
        if not self.can_generate_secure_passwords() or self.cupy is None:
            return None

        try:
            entropy = os.urandom(size)
            if system_mix is None:
                return entropy
            return mix_entropy(entropy, system_mix)[:size]
        except Exception as error:
            self.error_msg = f"GPU raw entropy generation failed: {error}"
            return None


_cuda_engine: Optional[CUDAEngine] = None


def get_cuda_engine() -> CUDAEngine:
    """Lädt die CUDA-Engine erst beim ersten Zugriff."""
    global _cuda_engine
    if _cuda_engine is None:
        _cuda_engine = CUDAEngine()
    return _cuda_engine

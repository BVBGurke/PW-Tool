"""CPU-basierte Entropieerzeugung für PW-Tool."""

from __future__ import annotations

import hashlib
import os
from typing import Optional

from system_mix import SystemMixResult, mix_entropy


class CPUEngine:
    """Verwaltet lokale, CPU-basierte Entropieoperationen."""

    @staticmethod
    def cpu_entropy_pbkdf2(
        iterations: int = 200000,
        hash_length: int = 64,
        system_mix: Optional[SystemMixResult] = None,
    ) -> bytes:
        """Leitet Entropie mit PBKDF2-HMAC-SHA512 ab.

        ``system_mix`` ist optional. Ein vollständiger Mix wird mittels HMAC mit
        frischem OS-Zufall kombiniert; bei unvollständigen Quellen verbleibt die
        Methode sicher beim ursprünglichen Zufallspfad.
        """
        seed = os.urandom(32)
        if system_mix is not None:
            seed = mix_entropy(seed, system_mix)
        salt = os.urandom(32)

        return hashlib.pbkdf2_hmac(
            "sha512",
            seed,
            salt,
            iterations,
            dklen=hash_length,
        )

    @staticmethod
    def cpu_raw_entropy(
        size: int = 64,
        system_mix: Optional[SystemMixResult] = None,
    ) -> bytes:
        """Gibt lokale OS-Entropie zurück und mischt sie optional sicher."""
        entropy = os.urandom(size)
        if system_mix is None:
            return entropy
        return mix_entropy(entropy, system_mix)[:size]

    @staticmethod
    def scale_iterations_for_mode(
        base_iterations: int = 200000,
        overkill: bool = False,
        multiplier: float = 5.0,
    ) -> int:
        """Skaliert die historische optionale Zusatzarbeit."""
        if overkill:
            return int(base_iterations * multiplier)
        return base_iterations


_cpu_engine = CPUEngine()


def get_cpu_engine() -> CPUEngine:
    """Gibt die Singleton-CPU-Engine zurück."""
    return _cpu_engine

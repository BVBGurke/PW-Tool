"""
CPU-Based Entropy Generation (Fallback for no CUDA).

This module provides CPU-only entropy derivation using standard hashlib PBKDF2.
Used when CUDA is unavailable or as a backup for reliable password generation.
"""

import hashlib
import os
from typing import Optional


class CPUEngine:
    """Manages CPU-based entropy operations."""

    @staticmethod
    def cpu_entropy_pbkdf2(
        iterations: int = 200000,
        hash_length: int = 64
    ) -> bytes:
        """
        Generate high-entropy bytes using CPU PBKDF2-HMAC-SHA512.
        
        Args:
            iterations: Number of PBKDF2 iterations
            hash_length: Output length in bytes (default 64 for SHA512)
            
        Returns:
            64 bytes of cryptographic entropy.
        """
        # Generate seed and salt from OS entropy
        seed = os.urandom(32)
        salt = os.urandom(32)
        
        # PBKDF2-HMAC-SHA512 with configurable iterations
        entropy = hashlib.pbkdf2_hmac(
            'sha512',
            seed,
            salt,
            iterations,
            dklen=hash_length
        )
        
        return entropy

    @staticmethod
    def cpu_raw_entropy(size: int = 64) -> bytes:
        """
        Generate raw entropy bytes from OS entropy pool.
        
        Args:
            size: Number of bytes to generate
            
        Returns:
            Random bytes from os.urandom.
        """
        return os.urandom(size)

    @staticmethod
    def scale_iterations_for_mode(
        base_iterations: int = 200000,
        overkill: bool = False,
        multiplier: float = 5.0
    ) -> int:
        """
        Scale iteration count for normal vs. overkill mode.
        
        Args:
            base_iterations: Base iteration count for normal mode
            overkill: If True, multiply by multiplier
            multiplier: Multiplier for overkill mode (default 5x)
            
        Returns:
            Scaled iteration count.
        """
        if overkill:
            return int(base_iterations * multiplier)
        return base_iterations


# Global singleton instance
_cpu_engine = CPUEngine()


def get_cpu_engine() -> CPUEngine:
    """Return the global CPU engine instance."""
    return _cpu_engine

"""Begrenzte, selbstbezogene scrypt-Demonstration ohne Angriffsfunktion."""

from __future__ import annotations

import hashlib
import hmac
import os
from time import perf_counter

from ..core.password_policy import generate_batch, validate_request


class HashDemoService:
    def run(self, length: int, charset: str) -> dict[str, object]:
        validate_request(length, 1, charset)
        demo_value = generate_batch(length, 1, charset)[0]
        salt = os.urandom(16)
        start = perf_counter()
        derived = hashlib.scrypt(demo_value.encode(), salt=salt, n=2**14, r=8, p=1, maxmem=64 * 1024 * 1024, dklen=32)
        verified = hmac.compare_digest(
            hashlib.scrypt(demo_value.encode(), salt=salt, n=2**14, r=8, p=1, maxmem=64 * 1024 * 1024, dklen=32),
            derived,
        )
        duration_ms = (perf_counter() - start) * 1000
        return {
            "algorithm": "scrypt", "n": 16384, "r": 8, "p": 1, "salt_bytes": 16,
            "output_bytes": 32, "duration_ms": round(duration_ms, 1), "verified": verified,
            "notice": "self-generated local demo only",
        }

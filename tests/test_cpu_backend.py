from __future__ import annotations

import unittest

from backends.base import BackendKind, GenerationRequest
from backends.cpu import CpuBackend
from password_engine import CharacterSet, PasswordGenerator


class CpuBackendTests(unittest.TestCase):
    def test_cpu_backend_generates_valid_batch_and_reports_phases(self) -> None:
        result = CpuBackend().generate(
            GenerationRequest(
                password_count=3,
                password_length=16,
                charset=CharacterSet.COMPLETE,
                iterations=1,
                system_mix_enabled=False,
            )
        )

        self.assertEqual(BackendKind.CPU, result.backend)
        self.assertEqual(3, len(result.passwords))
        self.assertTrue(all(len(password) == 16 for password in result.passwords))
        self.assertTrue(
            all(
                all(character in PasswordGenerator.CHARS_COMPLETE for character in password)
                for password in result.passwords
            )
        )
        self.assertEqual({"system_mix", "cpu_pbkdf2", "password_derivation"}, set(result.phase_seconds))


if __name__ == "__main__":
    unittest.main()

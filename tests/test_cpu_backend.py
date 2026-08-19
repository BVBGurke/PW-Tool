from __future__ import annotations

import unittest

from backends.base import BackendKind, GenerationRequest
from backends.cpu import CpuBackend
from password_engine import CharacterSet, PasswordGenerator


class CpuBackendTests(unittest.TestCase):
    def test_maximum_security_profile_uses_direct_os_csprng_path(self) -> None:
        result = CpuBackend().generate(
            GenerationRequest(
                password_count=3,
                password_length=32,
                charset=CharacterSet.MAXIMUM,
                iterations=1,
                system_mix_enabled=True,
            )
        )

        self.assertEqual(BackendKind.CPU, result.backend)
        self.assertEqual(3, len(result.passwords))
        self.assertTrue(all(len(password) == 32 for password in result.passwords))
        self.assertTrue(result.system_mix.status.value == "disabled")
        self.assertEqual({"os_csprng_password_generation"}, set(result.phase_seconds))
        self.assertTrue(
            all(
                any(character.islower() for character in password)
                and any(character.isupper() for character in password)
                and any(character.isdigit() for character in password)
                and any(not character.isalnum() for character in password)
                for password in result.passwords
            )
        )

    def test_cpu_backend_generates_direct_policy_batch_and_reports_phase(self) -> None:
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
        self.assertEqual({"os_csprng_password_generation"}, set(result.phase_seconds))
        self.assertEqual("disabled", result.system_mix.status.value)


if __name__ == "__main__":
    unittest.main()

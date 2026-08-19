from __future__ import annotations

import unittest

from password_engine import CharacterSet, PasswordGenerator
from security_check import assess_generated_passwords


class FirstRejectedThenAcceptedBytes:
    """Liefert zunächst einen zu verwerfenden Bytewert und anschließend null."""

    def __call__(self, size: int) -> bytes:
        return bytes([255, 0]) + bytes([255]) * (size - 2)


class MaximumSecurityGeneratorTests(unittest.TestCase):
    def test_maximum_password_has_all_required_classes(self) -> None:
        password = PasswordGenerator.generate_maximum(32)

        self.assertEqual(32, len(password))
        self.assertTrue(any(character.islower() for character in password))
        self.assertTrue(any(character.isupper() for character in password))
        self.assertTrue(any(character.isdigit() for character in password))
        self.assertTrue(any(not character.isalnum() for character in password))
        self.assertTrue(all(character in PasswordGenerator.CHARS_COMPLETE for character in password))

    def test_maximum_batch_is_independent_and_reported_as_os_csprng_profile(self) -> None:
        passwords = PasswordGenerator.generate_maximum_batch(8, 32)
        report = assess_generated_passwords(tuple(passwords), CharacterSet.MAXIMUM)

        self.assertEqual(8, len(set(passwords)))
        self.assertTrue(report.all_distinct)
        self.assertTrue(report.all_passwords_have_expected_classes)
        self.assertIn("direkter OS-CSPRNG", report.as_text())
        self.assertIn("konservative Untergrenze", report.as_text())
        self.assertGreater(report.estimated_entropy_bits, 190)
        self.assertLess(report.estimated_entropy_bits, 195)
        self.assertTrue(all(password not in report.as_text() for password in passwords))

    def test_rejection_sampling_discards_out_of_range_byte(self) -> None:
        index = PasswordGenerator._uniform_index(62, FirstRejectedThenAcceptedBytes())

        self.assertEqual(0, index)

    def test_maximum_profile_rejects_short_lengths(self) -> None:
        with self.assertRaisesRegex(ValueError, "16-256"):
            PasswordGenerator.generate_maximum(15)


if __name__ == "__main__":
    unittest.main()

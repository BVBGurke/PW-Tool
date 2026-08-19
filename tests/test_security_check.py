from __future__ import annotations

import unittest

from password_engine import CharacterSet
from security_check import assess_generated_passwords


class PasswordSecurityCheckTests(unittest.TestCase):
    def test_normal_generated_length_is_assessed_without_password_output(self) -> None:
        password = "Aa0" * 5 + "A"

        report = assess_generated_passwords((password,), CharacterSet.NORMAL)

        self.assertEqual(16, report.minimum_length)
        self.assertEqual(62, report.alphabet_size)
        self.assertGreater(report.estimated_entropy_bits, 95)
        self.assertEqual("ausreichend", report.rating)
        self.assertTrue(report.all_distinct)
        self.assertTrue(report.all_passwords_have_expected_classes)
        self.assertNotIn(password, report.as_text())

    def test_duplicate_values_are_reported_without_including_them(self) -> None:
        password = "Aa0" * 7

        report = assess_generated_passwords((password, password), CharacterSet.NORMAL)

        self.assertFalse(report.all_distinct)
        self.assertIn("gleiche Werte", report.advice)
        self.assertNotIn(password, report.as_text())

    def test_empty_input_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            assess_generated_passwords((), CharacterSet.COMPLETE)


if __name__ == "__main__":
    unittest.main()

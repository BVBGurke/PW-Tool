from __future__ import annotations

import unittest

from password_engine import CharacterSet, PasswordGenerator


class VisiblePasswordPolicyTests(unittest.TestCase):
    def test_compatible_policy_guarantees_only_compatible_classes(self) -> None:
        password = PasswordGenerator.generate_policy(32, CharacterSet.NORMAL)

        self.assertTrue(any(character.islower() for character in password))
        self.assertTrue(any(character.isupper() for character in password))
        self.assertTrue(any(character.isdigit() for character in password))
        self.assertTrue(all(character.isalnum() for character in password))

    def test_complete_policy_guarantees_all_classes(self) -> None:
        password = PasswordGenerator.generate_policy(32, CharacterSet.COMPLETE)

        self.assertTrue(any(character.islower() for character in password))
        self.assertTrue(any(character.isupper() for character in password))
        self.assertTrue(any(character.isdigit() for character in password))
        self.assertTrue(any(not character.isalnum() for character in password))
        self.assertTrue(all(character in PasswordGenerator.CHARS_COMPLETE for character in password))

    def test_short_visible_policy_passwords_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "16-256"):
            PasswordGenerator.generate_policy(15, CharacterSet.COMPLETE)


if __name__ == "__main__":
    unittest.main()

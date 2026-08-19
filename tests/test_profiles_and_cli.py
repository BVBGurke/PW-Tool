from __future__ import annotations

from pathlib import Path
import unittest

from profiles import ProfileOption, SessionProfiles
from pw import parse_args

class ProfilesAndCliTests(unittest.TestCase):
    def test_single_selection_sets_exact_active_options(self) -> None:
        profiles = SessionProfiles.from_selection("2")

        self.assertFalse(profiles.is_enabled(ProfileOption.GPU_FIRST))
        self.assertTrue(profiles.is_enabled(ProfileOption.BENCHMARK_METRICS))

    def test_empty_single_selection_uses_safe_default(self) -> None:
        profiles = SessionProfiles.from_selection("")

        self.assertTrue(profiles.is_enabled(ProfileOption.GPU_FIRST))
        self.assertFalse(profiles.is_enabled(ProfileOption.BENCHMARK_METRICS))

    def test_unavailable_profile_number_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SessionProfiles.from_selection("3")

    def test_log_is_explicit_opt_in(self) -> None:
        disabled = parse_args([])
        enabled = parse_args(["-log", "--log-directory", "diagnostics"])

        self.assertFalse(disabled.log_enabled)
        self.assertTrue(enabled.log_enabled)
        self.assertEqual(Path("diagnostics"), enabled.log_directory)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
import unittest

from profiles import ProfileOption, SessionProfiles
from pw import parse_args


class ProfilesAndCliTests(unittest.TestCase):
    def test_number_sequence_toggles_effective_options_only(self) -> None:
        profiles = SessionProfiles()
        self.assertTrue(profiles.is_enabled(ProfileOption.GPU_FIRST))
        self.assertFalse(profiles.is_enabled(ProfileOption.BENCHMARK_METRICS))

        profiles.toggle("1, 2")

        self.assertFalse(profiles.is_enabled(ProfileOption.GPU_FIRST))
        self.assertTrue(profiles.is_enabled(ProfileOption.BENCHMARK_METRICS))

    def test_unavailable_profile_number_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SessionProfiles().toggle("3")

    def test_log_is_explicit_opt_in(self) -> None:
        disabled = parse_args([])
        enabled = parse_args(["-log", "--log-directory", "diagnostics"])

        self.assertFalse(disabled.log_enabled)
        self.assertTrue(enabled.log_enabled)
        self.assertEqual(Path("diagnostics"), enabled.log_directory)


if __name__ == "__main__":
    unittest.main()

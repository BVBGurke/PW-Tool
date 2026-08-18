from __future__ import annotations

from io import StringIO
from pathlib import Path
import unittest

from profiles import ProfileOption, SessionProfiles
from pw import parse_args
from tui import RichUI

try:
    from rich.console import Console
except ImportError:  # pragma: no cover - runtime dependency is mandatory
    Console = None


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

    @unittest.skipIf(Console is None, "Rich is not installed")
    def test_compact_output_folds_without_ellipsis_or_table(self) -> None:
        output = StringIO()
        console = Console(file=output, width=40, force_terminal=False, color_system=None)
        ui = RichUI(cuda_available=False, console=console)
        value = "AbC123XyZ" * 12
        ui.computation_time = 0.1

        ui.show_header()
        ui.show_backend_decision("cpu", "CUDA nicht verfügbar", logging_enabled=False)
        ui.display_passwords([value], "CPU")

        rendered = output.getvalue()
        self.assertNotIn("┏", rendered)
        self.assertNotIn("…", rendered)
        self.assertIn(value, rendered.replace("\n", ""))
        self.assertIn("Backend: CPU", rendered)


if __name__ == "__main__":
    unittest.main()

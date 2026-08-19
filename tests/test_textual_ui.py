from __future__ import annotations

import unittest
from unittest.mock import patch

from backends.base import BackendKind, GenerationResult
from dispatcher import BackendDecision
from hash_demo import LocalHashDemoReport
from password_engine import CharacterSet
from system_mix import SystemMixResult
from textual_ui import PwToolTextualApp


class TextualUiTests(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def _fake_generate(
        count: int,
        length: int,
        charset: CharacterSet,
        extra_kdf_work: bool,
        system_mix_enabled: bool,
        _profiles: object,
    ) -> tuple[GenerationResult, BackendDecision]:
        del extra_kdf_work, system_mix_enabled
        unit = "Ab9[mark]*" if charset is CharacterSet.COMPLETE else "Ab9mark"
        value = (unit * ((length + len(unit) - 1) // len(unit)))[:length]
        result = GenerationResult(
            passwords=[value for _ in range(count)],
            backend=BackendKind.CPU,
            system_mix=SystemMixResult.disabled(),
            phase_seconds={"os_csprng_password_generation": 0.001},
        )
        return result, BackendDecision(BackendKind.CPU, "Direkter Test-CSPRNG-Pfad")

    def _app(self) -> PwToolTextualApp:
        return PwToolTextualApp(
            self._fake_generate,
            cuda_available=False,
            device_name="",
            log_enabled=False,
        )

    async def test_compact_layout_has_only_core_settings_and_full_result_text(self) -> None:
        app = self._app()
        expected = ("Ab9[mark]*" * 7)[:64]

        async with app.run_test(size=(40, 30)) as pilot:
            await pilot.pause()
            self.assertTrue(app.screen.has_class("compact"))
            self.assertEqual(CharacterSet.COMPLETE.value, str(app.query_one("#charset").value))
            self.assertEqual(0, len(list(app.query("#system-mix"))))
            self.assertEqual(0, len(list(app.query("#extra-kdf"))))
            self.assertEqual(0, len(list(app.query("#show-metrics"))))
            self.assertEqual(0, len(list(app.query("#cuda-candidate"))))

            app.action_generate()
            await pilot.pause()
            rendered = str(app.query_one("#results").render())
            self.assertIn(expected, rendered)
            self.assertNotIn("…", rendered)
            self.assertFalse(app.query_one("#copy").disabled)
            self.assertFalse(app.query_one("#check").disabled)
            self.assertFalse(app.query_one("#clear").disabled)

            app.action_check_passwords()
            await pilot.pause()
            security_report = str(app.query_one("#security-check").render())
            self.assertIn("Sicherheitscheck (nur lokal)", security_report)
            self.assertIn("vollständiger Zeichenvorrat", security_report)
            self.assertNotIn(expected, security_report)

            app.action_clear_passwords()
            await pilot.pause()
            self.assertTrue(app.query_one("#copy").disabled)
            self.assertTrue(app.query_one("#check").disabled)
            self.assertTrue(app.query_one("#clear").disabled)
            self.assertIn(
                "Ergebnisse aus der Oberfläche entfernt.",
                str(app.query_one("#results").render()),
            )

    async def test_hash_demo_shows_only_safe_metadata(self) -> None:
        app = self._app()
        report = LocalHashDemoReport(
            algorithm="scrypt",
            n=16384,
            r=8,
            p=1,
            salt_length=16,
            derived_key_length=32,
            duration_ms=12.3,
            self_verification_passed=True,
            execution_path="CPU-scrypt mit frischem OS-CSPRNG-Salt",
            accelerator_status="Android/Termux erkannt; sicherer CPU-Fallback aktiv",
        )

        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause()
            with patch("textual_ui.run_local_hash_demo", return_value=report):
                app.action_run_hash_demo()
                await pilot.pause()
            rendered = str(app.query_one("#hash-demo").render())
            self.assertIn("Hash-Demo (nur lokal, kein Crack-Versuch)", rendered)
            self.assertIn("scrypt", rendered)
            self.assertIn("Android/Termux", rendered)
            self.assertNotIn("Ab9[mark]*", rendered)

    async def test_invalid_form_prevents_generation(self) -> None:
        app = self._app()

        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause()
            app.query_one("#password-length").value = "15"
            app.action_generate()
            await pilot.pause()
            status = str(app.query_one("#status").render())
            self.assertIn("Länge muss 16–256", status)
            self.assertIn("invalid", app.query_one("#password-length").classes)


if __name__ == "__main__":
    unittest.main()

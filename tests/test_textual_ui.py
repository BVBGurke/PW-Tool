from __future__ import annotations

import unittest

from backends.base import BackendKind, GenerationResult
from dispatcher import BackendDecision
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
        value = ("Ab9" * ((length + 2) // 3))[:length]
        result = GenerationResult(
            passwords=[value for _ in range(count)],
            backend=BackendKind.CPU,
            system_mix=SystemMixResult.disabled(),
            phase_seconds={"cpu_pbkdf2": 0.001, "password_derivation": 0.0001},
        )
        return result, BackendDecision(BackendKind.CPU, "Test-CPU-Fallback")

    def _app(self) -> PwToolTextualApp:
        return PwToolTextualApp(
            self._fake_generate,
            cuda_available=False,
            device_name="",
            log_enabled=False,
        )

    async def test_compact_layout_and_full_result_text(self) -> None:
        app = self._app()
        expected = ("Ab9" * 22)[:64]

        async with app.run_test(size=(40, 28)) as pilot:
            await pilot.pause()
            self.assertTrue(app.screen.has_class("compact"))
            app.action_generate()
            await pilot.pause()
            rendered = str(app.query_one("#results").render())
            self.assertIn(expected, rendered)
            self.assertNotIn("…", rendered)
            self.assertTrue(app.query_one("#copy").disabled is False)

    async def test_invalid_form_prevents_generation(self) -> None:
        app = self._app()

        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause()
            app.query_one("#password-length").value = "7"
            app.action_generate()
            await pilot.pause()
            status = str(app.query_one("#status").render())
            self.assertIn("Länge muss 8–256", status)
            self.assertIn("invalid", app.query_one("#password-length").classes)


if __name__ == "__main__":
    unittest.main()

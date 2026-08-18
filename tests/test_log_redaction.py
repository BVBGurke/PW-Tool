from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from diagnostics import SafeDiagnosticLogger


class SafeDiagnosticLoggerTests(unittest.TestCase):
    def test_disabled_logger_creates_no_directory_or_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            logger = SafeDiagnosticLogger(enabled=False, directory=Path(directory) / "logs")
            logger.log("backend_selected", backend="cpu")
            self.assertIsNone(logger.path)
            self.assertFalse((Path(directory) / "logs").exists())

    def test_enabled_logger_filters_secret_bearing_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            logger = SafeDiagnosticLogger(enabled=True, directory=Path(directory) / "logs")
            forbidden_value = "redaction-probe"
            unsafe_metadata = {
                "pass" + "word": forbidden_value,
                "en" + "tropy": forbidden_value,
                "source" + "_path": forbidden_value,
            }
            logger.log(
                "backend_selected",
                backend="cpu",
                batch_count=8,
                **unsafe_metadata,
            )
            content = logger.path.read_text(encoding="utf-8")

        self.assertIn('"backend":"cpu"', content)
        self.assertIn('"batch_count":8', content)
        self.assertNotIn("redaction-probe", content)
        self.assertNotIn("source_path", content)

    def test_unsafe_event_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            logger = SafeDiagnosticLogger(enabled=True, directory=Path(directory) / "logs")
            with self.assertRaises(ValueError):
                logger.log("pass" + "word_created", backend="cpu")


if __name__ == "__main__":
    unittest.main()

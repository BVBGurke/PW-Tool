from __future__ import annotations

import inspect
import os
import unittest
from unittest.mock import patch

from hash_demo import LocalHashDemoReport, run_local_hash_demo
from password_engine import CharacterSet


class _UnavailableCuda:
    available = False


class HashDemoTests(unittest.TestCase):
    def test_demo_reports_only_safe_metadata(self) -> None:
        report = run_local_hash_demo(16, CharacterSet.COMPLETE)
        rendered = report.as_text()

        self.assertTrue(report.self_verification_passed)
        self.assertEqual("scrypt", report.algorithm)
        self.assertEqual(16, report.salt_length)
        self.assertEqual(32, report.derived_key_length)
        self.assertIn("kein Crack-Versuch", rendered)
        self.assertIn("CPU-scrypt", rendered)
        self.assertNotIn("password", report.__dict__)
        self.assertNotIn("salt", report.__dict__)
        self.assertNotIn("derived", report.__dict__)

    def test_demo_has_no_foreign_hash_or_candidate_inputs(self) -> None:
        parameters = tuple(inspect.signature(run_local_hash_demo).parameters)

        self.assertEqual(("length", "charset"), parameters)

    def test_android_reports_safe_cpu_fallback(self) -> None:
        with patch("hash_demo.get_cuda_engine", return_value=_UnavailableCuda()):
            with patch.dict(os.environ, {"TERMUX_VERSION": "0.118"}, clear=False):
                report = run_local_hash_demo(16, CharacterSet.NORMAL)

        self.assertIn("Android/Termux", report.accelerator_status)
        self.assertIn("CPU-Fallback", report.accelerator_status)
        self.assertIsInstance(report, LocalHashDemoReport)


if __name__ == "__main__":
    unittest.main()

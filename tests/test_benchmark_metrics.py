from __future__ import annotations

import unittest

from benchmark.metrics import RunMeasurement, summarize
from benchmark.runner import BenchmarkRunner, PhaseRecorder


class BenchmarkMetricsTests(unittest.TestCase):
    def test_summary_reports_median_percentiles_and_throughput(self) -> None:
        measurements = [
            RunMeasurement("cpu", "small", 1.0, {}, None),
            RunMeasurement("cpu", "small", 2.0, {}, None),
            RunMeasurement("cpu", "small", 3.0, {}, None),
        ]

        result = summarize(measurements, units_per_run=6)

        self.assertEqual(3, result.count)
        self.assertEqual(2.0, result.median_seconds)
        self.assertGreaterEqual(result.p95_seconds, result.median_seconds)
        self.assertEqual(3.0, result.throughput_per_second)

    def test_runner_executes_warmups_and_collects_named_phases(self) -> None:
        calls = []

        def operation(recorder: PhaseRecorder) -> None:
            calls.append(True)
            with recorder.phase("cpu_prepare"):
                sum(range(100))
            with recorder.phase("derive"):
                sum(range(100))

        result = BenchmarkRunner().run(
            backend="cpu",
            workload="single",
            units_per_run=1,
            operation=operation,
            warmups=2,
            repeats=3,
            capture_python_memory=True,
        )

        self.assertEqual(5, len(calls))
        self.assertEqual(3, result.summary.count)
        self.assertIn("cpu_prepare", result.phase_median_seconds)
        self.assertIn("derive", result.phase_median_seconds)
        self.assertIsNotNone(result.summary.peak_python_bytes)


if __name__ == "__main__":
    unittest.main()

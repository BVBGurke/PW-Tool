"""Mess-Harness für End-to-End- und Phasen-Benchmarks ohne Secret-Ausgabe."""

from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from time import perf_counter
import tracemalloc
from typing import Callable, Iterator, Mapping, Optional

from benchmark.metrics import LatencySummary, RunMeasurement, summarize


class PhaseRecorder:
    """Erfasst additive, benannte Phasen einer einzelnen Messung."""

    def __init__(self) -> None:
        self._durations: dict[str, float] = defaultdict(float)

    @contextmanager
    def phase(self, name: str) -> Iterator[None]:
        start = perf_counter()
        try:
            yield
        finally:
            self._durations[name] += perf_counter() - start

    def add_duration(self, name: str, seconds: float) -> None:
        """Übernimmt eine vom Backend bereits separat gemessene Phase."""
        if seconds < 0:
            raise ValueError("seconds must not be negative")
        self._durations[name] += seconds

    def snapshot(self) -> dict[str, float]:
        return dict(self._durations)


BenchmarkOperation = Callable[[PhaseRecorder], None]


@dataclass(frozen=True)
class BenchmarkResult:
    backend: str
    workload: str
    warmups: int
    summary: LatencySummary
    phase_median_seconds: Mapping[str, float]

    def to_dict(self) -> dict:
        return {
            "backend": self.backend,
            "workload": self.workload,
            "warmups": self.warmups,
            "summary": self.summary.to_dict(),
            "phase_median_seconds": dict(self.phase_median_seconds),
        }


class BenchmarkRunner:
    """Führt kalte/warmgelaufene, wiederholte Messungen aus."""

    def run(
        self,
        *,
        backend: str,
        workload: str,
        units_per_run: int,
        operation: BenchmarkOperation,
        warmups: int = 1,
        repeats: int = 7,
        capture_python_memory: bool = False,
    ) -> BenchmarkResult:
        if warmups < 0:
            raise ValueError("warmups must not be negative")
        if repeats < 1:
            raise ValueError("repeats must be at least one")

        for _ in range(warmups):
            operation(PhaseRecorder())

        measurements = [
            self._measure_once(
                backend=backend,
                workload=workload,
                operation=operation,
                capture_python_memory=capture_python_memory,
            )
            for _ in range(repeats)
        ]
        return BenchmarkResult(
            backend=backend,
            workload=workload,
            warmups=warmups,
            summary=summarize(measurements, units_per_run),
            phase_median_seconds=self._phase_medians(measurements),
        )

    def _measure_once(
        self,
        *,
        backend: str,
        workload: str,
        operation: BenchmarkOperation,
        capture_python_memory: bool,
    ) -> RunMeasurement:
        recorder = PhaseRecorder()
        if capture_python_memory:
            tracemalloc.start()
        start = perf_counter()
        try:
            operation(recorder)
        finally:
            total = perf_counter() - start
            if capture_python_memory:
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
            else:
                peak = None

        return RunMeasurement(
            backend=backend,
            workload=workload,
            total_seconds=total,
            phase_seconds=recorder.snapshot(),
            peak_python_bytes=peak,
        )

    @staticmethod
    def _phase_medians(measurements: list[RunMeasurement]) -> dict[str, float]:
        all_phases: dict[str, list[float]] = defaultdict(list)
        for measurement in measurements:
            for phase, duration in measurement.phase_seconds.items():
                all_phases[phase].append(duration)
        return {
            phase: sorted(values)[len(values) // 2]
            for phase, values in all_phases.items()
        }

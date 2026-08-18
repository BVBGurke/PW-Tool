"""Reproduzierbare, secret-freie Performance-Metriken für PW-Tool."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import fmean, median
from typing import Mapping, Sequence


@dataclass(frozen=True)
class RunMeasurement:
    """Eine einzelne End-to-End-Messung ohne Passwort- oder Entropiedaten."""

    backend: str
    workload: str
    total_seconds: float
    phase_seconds: Mapping[str, float]
    peak_python_bytes: int | None

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "phase_seconds": dict(self.phase_seconds),
        }


@dataclass(frozen=True)
class LatencySummary:
    """Zusammenfassung wiederholter, bereits aufgewärmter Läufe."""

    count: int
    minimum_seconds: float
    mean_seconds: float
    median_seconds: float
    p95_seconds: float
    p99_seconds: float
    maximum_seconds: float
    throughput_per_second: float
    peak_python_bytes: int | None

    def to_dict(self) -> dict:
        return asdict(self)


def summarize(measurements: Sequence[RunMeasurement], units_per_run: int) -> LatencySummary:
    """Berechnet Latenz- und Durchsatzwerte ohne externe Abhängigkeit."""
    if not measurements:
        raise ValueError("At least one measurement is required")
    if units_per_run < 1:
        raise ValueError("units_per_run must be at least one")

    values = sorted(measurement.total_seconds for measurement in measurements)
    average = fmean(values)
    median_value = median(values)
    peak_values = [m.peak_python_bytes for m in measurements if m.peak_python_bytes is not None]

    return LatencySummary(
        count=len(values),
        minimum_seconds=values[0],
        mean_seconds=average,
        median_seconds=median_value,
        p95_seconds=_percentile(values, 0.95),
        p99_seconds=_percentile(values, 0.99),
        maximum_seconds=values[-1],
        throughput_per_second=units_per_run / median_value if median_value > 0 else float("inf"),
        peak_python_bytes=max(peak_values) if peak_values else None,
    )


def _percentile(sorted_values: Sequence[float], percentile: float) -> float:
    """Berechnet eine linear interpolierte Perzentil-Schätzung."""
    if not sorted_values:
        raise ValueError("sorted_values must not be empty")
    if not 0.0 <= percentile <= 1.0:
        raise ValueError("percentile must be in range 0.0..1.0")

    position = (len(sorted_values) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction

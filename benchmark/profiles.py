"""Vordefinierte Workload-Klassen für reproduzierbare PW-Tool-Benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WorkloadClass(str, Enum):
    SINGLE = "single"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass(frozen=True)
class BenchmarkProfile:
    name: WorkloadClass
    password_count: int
    password_length: int
    iterations: int


PROFILES: dict[WorkloadClass, BenchmarkProfile] = {
    WorkloadClass.SINGLE: BenchmarkProfile(WorkloadClass.SINGLE, 1, 24, 200_000),
    WorkloadClass.SMALL: BenchmarkProfile(WorkloadClass.SMALL, 8, 24, 200_000),
    WorkloadClass.MEDIUM: BenchmarkProfile(WorkloadClass.MEDIUM, 128, 32, 200_000),
    WorkloadClass.LARGE: BenchmarkProfile(WorkloadClass.LARGE, 1_024, 32, 200_000),
}


def resolve_profile(name: str | WorkloadClass) -> BenchmarkProfile:
    """Löst einen Profilnamen ohne dynamische oder geheime Eingabedaten auf."""
    try:
        workload = name if isinstance(name, WorkloadClass) else WorkloadClass(name.lower())
    except ValueError as error:
        supported = ", ".join(item.value for item in WorkloadClass)
        raise ValueError(f"Unknown workload '{name}'. Supported: {supported}") from error
    return PROFILES[workload]

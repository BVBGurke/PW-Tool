"""Gemeinsame Schnittstellen für sichere PW-Tool-Backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Protocol

from password_engine import CharacterSet, MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from system_mix import SystemMixResult


MAX_BATCH_COUNT = 10_000


class BackendKind(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"


@dataclass(frozen=True)
class GenerationRequest:
    """Nicht geheime Konfiguration eines Passwort-Batches."""

    password_count: int
    password_length: int
    charset: CharacterSet
    iterations: int
    system_mix_enabled: bool

    def __post_init__(self) -> None:
        if self.password_count < 1 or self.password_count > MAX_BATCH_COUNT:
            raise ValueError(f"password_count must be in range 1..{MAX_BATCH_COUNT}")
        if not MIN_PASSWORD_LENGTH <= self.password_length <= MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"password_length must be in range {MIN_PASSWORD_LENGTH}..{MAX_PASSWORD_LENGTH}"
            )
        if self.iterations < 1:
            raise ValueError("iterations must be at least one")


@dataclass(frozen=True)
class GenerationResult:
    """Ergebnis eines Backends ohne Seed- oder Entropiepreisgabe."""

    passwords: list[str]
    backend: BackendKind
    system_mix: SystemMixResult
    phase_seconds: Mapping[str, float] = field(default_factory=dict)
    worker_count: int = 1


class GenerationBackend(Protocol):
    """Ausführbare Backend-Schnittstelle mit expliziter Verfügbarkeit."""

    kind: BackendKind

    def is_available(self) -> bool:
        """Gibt an, ob das Backend auf der aktuellen Plattform ausführbar ist."""

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Erzeugt Passwörter ohne Nebenwirkungen in Diagnoseausgaben."""

"""Wirksame, nicht persistierte Sitzungsoptionen für die PW-Tool-Beta."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProfileOption(str, Enum):
    """Nur Optionen, die die aktuelle Beta-Ausführung wirklich beeinflussen."""

    GPU_FIRST = "1"
    BENCHMARK_METRICS = "2"


_DEFAULT_ENABLED = frozenset({ProfileOption.GPU_FIRST})


@dataclass
class SessionProfiles:
    """Nicht persistierte Auswahl für genau eine CLI-Sitzung."""

    enabled: set[ProfileOption] = field(default_factory=lambda: set(_DEFAULT_ENABLED))

    @classmethod
    def from_selection(cls, selection: str) -> "SessionProfiles":
        """Erstellt die Auswahl aus einer einzigen Eingabe.

        Eine leere Eingabe behält die sichere Standardoption 1. Andernfalls
        aktiviert die Eingabe genau die durch Leerzeichen oder Komma getrennten
        Optionen; ein wiederholtes Umschalten ist nicht erforderlich.
        """
        values = [value for value in selection.replace(",", " ").split() if value]
        if not values:
            return cls()

        selected: set[ProfileOption] = set()
        for value in values:
            try:
                selected.add(ProfileOption(value))
            except ValueError as error:
                raise ValueError("Nur die aktuell verfügbaren Optionsnummern 1 und 2 sind erlaubt.") from error
        return cls(enabled=selected)

    def is_enabled(self, option: ProfileOption) -> bool:
        return option in self.enabled

    def labels(self) -> tuple[str, ...]:
        return tuple(sorted(option.value for option in self.enabled))

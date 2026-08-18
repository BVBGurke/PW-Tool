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

    def toggle(self, selection: str) -> tuple[ProfileOption, ...]:
        """Schaltet durch Leerzeichen/Komma getrennte verfügbare Optionen um."""
        values = [value for value in selection.replace(",", " ").split() if value]
        changed: list[ProfileOption] = []
        for value in values:
            try:
                option = ProfileOption(value)
            except ValueError as error:
                raise ValueError("Nur die aktuell verfügbaren Optionsnummern 1 und 2 sind erlaubt.") from error
            if option in self.enabled:
                self.enabled.remove(option)
            else:
                self.enabled.add(option)
            changed.append(option)
        return tuple(changed)

    def is_enabled(self, option: ProfileOption) -> bool:
        return option in self.enabled

    def labels(self) -> tuple[str, ...]:
        return tuple(sorted(option.value for option in self.enabled))

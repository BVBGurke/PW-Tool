"""Kleine, prozesslokale Schutzgrenze für Authentisierungs- und API-Spitzen."""

from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic
from typing import Deque


class MemoryRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: float) -> bool:
        now = monotonic()
        events = self._events[key]
        while events and now - events[0] > window_seconds:
            events.popleft()
        if len(events) >= limit:
            return False
        events.append(now)
        return True

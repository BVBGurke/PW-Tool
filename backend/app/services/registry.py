"""Expliziter Container für die Abhängigkeiten der Routen."""

from __future__ import annotations

from dataclasses import dataclass

from .auth import AuthService
from .capability import CapabilityService
from .hash_demo import HashDemoService
from .history import HistoryService
from .passwords import PasswordService


@dataclass(frozen=True)
class ServiceRegistry:
    auth: AuthService
    passwords: PasswordService
    history: HistoryService
    hash_demo: HashDemoService
    capability: CapabilityService

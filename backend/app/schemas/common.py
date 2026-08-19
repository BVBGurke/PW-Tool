"""Unkritische Systemantworten."""

from __future__ import annotations

from pydantic import BaseModel


class HealthOutput(BaseModel):
    status: str
    lan_enabled: bool

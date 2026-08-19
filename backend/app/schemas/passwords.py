"""Verträge für CSPRNG-Passworterzeugung und Sicherheitszusammenfassung."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GenerationInput(BaseModel):
    length: int = Field(default=64, ge=16, le=256)
    count: int = Field(default=1, ge=1, le=10_000)
    charset: Literal["normal", "complete"] = "complete"
    save_history: bool = False


class SecuritySummaryOutput(BaseModel):
    profile: Literal["normal", "complete"]
    minimum_length: int
    alphabet_size: int
    conservative_entropy_bits: float
    all_distinct: bool
    guaranteed_classes: int


class GenerationOutput(BaseModel):
    passwords: list[str]
    security: SecuritySummaryOutput
    saved: bool

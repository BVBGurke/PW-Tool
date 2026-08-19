"""Verträge für den opt-in verschlüsselten Verlauf."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HistoryEntryOutput(BaseModel):
    id: int
    password: str
    charset: Literal["normal", "complete"]
    created_at: str


class HistoryListOutput(BaseModel):
    entries: list[HistoryEntryOutput]

"""Verträge für lokale Konto- und Sitzungsvorgänge."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CredentialsInput(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=12, max_length=1024)


class AccountOutput(BaseModel):
    id: int
    username: str


class SessionOutput(BaseModel):
    account: AccountOutput

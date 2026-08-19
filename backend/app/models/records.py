"""Typisierte Datenträger zwischen Repository- und Service-Schicht."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountRecord:
    id: int
    username: str
    password_hash: str


@dataclass(frozen=True)
class HistoryRecord:
    id: int
    account_id: int
    nonce: bytes
    ciphertext: bytes
    charset: str
    created_at: str

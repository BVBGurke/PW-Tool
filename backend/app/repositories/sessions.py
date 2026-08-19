"""Serverseitige opaque Session-Persistenz."""

from __future__ import annotations

from datetime import datetime, timezone

from ..models.records import AccountRecord
from .accounts import AccountRepository
from .database import Database


class SessionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, digest: str, account_id: int, expires_at: str) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "INSERT INTO sessions(token_digest, account_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
                (digest, account_id, expires_at, datetime.now(timezone.utc).isoformat()),
            )

    def account_for_digest(self, digest: str) -> AccountRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.database.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
            row = connection.execute(
                "SELECT accounts.id, accounts.username, accounts.password_hash FROM sessions "
                "JOIN accounts ON accounts.id = sessions.account_id "
                "WHERE sessions.token_digest = ? AND sessions.expires_at > ?",
                (digest, now),
            ).fetchone()
        return AccountRepository._to_record(row)

    def delete(self, digest: str) -> None:
        with self.database.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_digest = ?", (digest,))

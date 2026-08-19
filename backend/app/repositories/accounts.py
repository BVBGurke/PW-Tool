"""Kontopersistenz ohne HTTP- oder KDF-Logik."""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

from ..models.records import AccountRecord
from .database import Database


class AccountRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, username: str, password_hash: str) -> AccountRecord:
        with self.database.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO accounts(username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, datetime.now(timezone.utc).isoformat()),
            )
            return AccountRecord(id=int(cursor.lastrowid), username=username, password_hash=password_hash)

    def by_username(self, username: str) -> AccountRecord | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT id, username, password_hash FROM accounts WHERE username = ?", (username,)
            ).fetchone()
        return self._to_record(row)

    @staticmethod
    def _to_record(row: sqlite3.Row | None) -> AccountRecord | None:
        if row is None:
            return None
        return AccountRecord(id=int(row["id"]), username=str(row["username"]), password_hash=str(row["password_hash"]))

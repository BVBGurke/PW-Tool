"""Kontogebundene Persistenz verschlüsselter Verlaufseinträge."""

from __future__ import annotations

from datetime import datetime, timezone

from ..models.records import HistoryRecord
from .database import Database


class HistoryRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, account_id: int, nonce: bytes, ciphertext: bytes, charset: str) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "INSERT INTO history_entries(account_id, nonce, ciphertext, charset, created_at) VALUES (?, ?, ?, ?, ?)",
                (account_id, nonce, ciphertext, charset, datetime.now(timezone.utc).isoformat()),
            )

    def for_account(self, account_id: int) -> list[HistoryRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT id, account_id, nonce, ciphertext, charset, created_at FROM history_entries "
                "WHERE account_id = ? ORDER BY id DESC LIMIT 100",
                (account_id,),
            ).fetchall()
        return [
            HistoryRecord(
                id=int(row["id"]), account_id=int(row["account_id"]), nonce=bytes(row["nonce"]),
                ciphertext=bytes(row["ciphertext"]), charset=str(row["charset"]), created_at=str(row["created_at"]),
            )
            for row in rows
        ]

    def delete_for_account(self, account_id: int, entry_id: int) -> bool:
        with self.database.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM history_entries WHERE id = ? AND account_id = ?", (entry_id, account_id)
            )
            return cursor.rowcount == 1

"""Entschlüsselung und Löschung ausschließlich eigener Verlaufseinträge."""

from __future__ import annotations

from ..core.exceptions import NotFoundError
from ..models.records import AccountRecord
from ..repositories.history import HistoryRepository
from ..security.history_crypto import decrypt_history_value


class HistoryService:
    def __init__(self, history: HistoryRepository, history_key: bytes) -> None:
        self.history = history
        self.history_key = history_key

    def list_for_account(self, account: AccountRecord) -> list[dict[str, object]]:
        return [
            {
                "id": entry.id,
                "password": decrypt_history_value(entry.nonce, entry.ciphertext, self.history_key, account.id),
                "charset": entry.charset,
                "created_at": entry.created_at,
            }
            for entry in self.history.for_account(account.id)
        ]

    def delete(self, account: AccountRecord, entry_id: int) -> None:
        if not self.history.delete_for_account(account.id, entry_id):
            raise NotFoundError()

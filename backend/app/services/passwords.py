"""Password-Generation-Service auf Basis der reinen CSPRNG-Policy."""

from __future__ import annotations

from ..core.password_policy import generate_batch, security_summary, validate_request
from ..models.records import AccountRecord
from ..repositories.history import HistoryRepository
from ..security.history_crypto import encrypt_history_value


class PasswordService:
    def __init__(self, history: HistoryRepository, history_key: bytes) -> None:
        self.history = history
        self.history_key = history_key

    def generate(self, account: AccountRecord, length: int, count: int, charset: str, save_history: bool) -> dict[str, object]:
        validate_request(length, count, charset)
        passwords = generate_batch(length, count, charset)
        if save_history:
            for password in passwords:
                nonce, ciphertext = encrypt_history_value(password, self.history_key, account.id)
                self.history.add(account.id, nonce, ciphertext, charset)
        return {"passwords": passwords, "security": security_summary(passwords, charset), "saved": save_history}

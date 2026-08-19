"""AES-GCM-Verlaufsschutz mit kontogebundener authentifizierter Datenbindung."""

from __future__ import annotations

import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_history_value(value: str, history_key: bytes, account_id: int) -> tuple[bytes, bytes]:
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(history_key).encrypt(nonce, value.encode("utf-8"), str(account_id).encode("ascii"))
    return nonce, ciphertext


def decrypt_history_value(nonce: bytes, ciphertext: bytes, history_key: bytes, account_id: int) -> str:
    return AESGCM(history_key).decrypt(nonce, ciphertext, str(account_id).encode("ascii")).decode("utf-8")

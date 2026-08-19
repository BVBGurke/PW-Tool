"""Kontokennwort-KDF, serverseitige Sitzungen und AEAD-Verlaufverschlüsselung."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ACCOUNT_N = 2**14
ACCOUNT_R = 8
ACCOUNT_P = 1
ACCOUNT_DKLEN = 32
ACCOUNT_SALT_BYTES = 16
ACCOUNT_MAXMEM = 64 * 1024 * 1024
SESSION_LIFETIME = timedelta(hours=12)


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))


def _password_bytes(password: str) -> bytes:
    encoded = password.encode("utf-8")
    if not 12 <= len(encoded) <= 1024:
        raise ValueError("account password must contain 12-1024 UTF-8 bytes")
    return encoded


def hash_account_password(password: str) -> str:
    salt = secrets.token_bytes(ACCOUNT_SALT_BYTES)
    derived = hashlib.scrypt(
        _password_bytes(password), salt=salt, n=ACCOUNT_N, r=ACCOUNT_R, p=ACCOUNT_P,
        maxmem=ACCOUNT_MAXMEM, dklen=ACCOUNT_DKLEN,
    )
    return f"scrypt${ACCOUNT_N}${ACCOUNT_R}${ACCOUNT_P}${_b64(salt)}${_b64(derived)}"


def verify_account_password(password: str, stored: str) -> bool:
    try:
        scheme, n, r, p, salt_raw, expected_raw = stored.split("$")
        if (scheme, n, r, p) != ("scrypt", str(ACCOUNT_N), str(ACCOUNT_R), str(ACCOUNT_P)):
            return False
        derived = hashlib.scrypt(
            _password_bytes(password), salt=_unb64(salt_raw), n=ACCOUNT_N, r=ACCOUNT_R, p=ACCOUNT_P,
            maxmem=ACCOUNT_MAXMEM, dklen=ACCOUNT_DKLEN,
        )
        return hmac.compare_digest(derived, _unb64(expected_raw))
    except (ValueError, UnicodeError, TypeError):
        return False


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def session_digest(token: str, session_key: bytes) -> str:
    return hmac.new(session_key, token.encode("utf-8"), hashlib.sha256).hexdigest()


def expiry_timestamp() -> str:
    return (datetime.now(timezone.utc) + SESSION_LIFETIME).isoformat()


def encrypt_history_value(value: str, history_key: bytes, account_id: int) -> tuple[bytes, bytes]:
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(history_key).encrypt(nonce, value.encode("utf-8"), str(account_id).encode("ascii"))
    return nonce, ciphertext


def decrypt_history_value(nonce: bytes, ciphertext: bytes, history_key: bytes, account_id: int) -> str:
    return AESGCM(history_key).decrypt(nonce, ciphertext, str(account_id).encode("ascii")).decode("utf-8")

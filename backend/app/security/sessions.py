"""Opaque, serverseitige Sessiontokens mit HMAC-gespeicherten Digests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets


SESSION_LIFETIME = timedelta(hours=12)


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def session_digest(token: str, session_key: bytes) -> str:
    return hmac.new(session_key, token.encode("utf-8"), hashlib.sha256).hexdigest()


def expiry_timestamp() -> str:
    return (datetime.now(timezone.utc) + SESSION_LIFETIME).isoformat()

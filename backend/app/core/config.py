"""Strikt validierte lokale und LAN-Konfiguration für PW-Tool."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_ORIGINS = ("http://127.0.0.1:5173", "http://localhost:5173")
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _decode_key(value: str, label: str) -> bytes:
    try:
        decoded = base64.urlsafe_b64decode(value.encode("ascii"))
    except Exception as error:
        raise ValueError(f"{label} is not valid URL-safe base64") from error
    if len(decoded) != 32:
        raise ValueError(f"{label} must decode to exactly 32 bytes")
    return decoded


def _as_bool(value: object, label: str) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError(f"{label} must be a boolean")


def _is_local_origin(origin: str) -> bool:
    host = urlparse(origin).hostname
    return host in {"127.0.0.1", "localhost", "::1"}


@dataclass(frozen=True)
class Settings:
    database_path: Path
    session_key: bytes
    history_key: bytes
    allowed_origins: tuple[str, ...]
    lan_enabled: bool
    cookie_secure: bool
    cookie_samesite: str

    @classmethod
    def from_mapping(cls, values: dict[str, object]) -> "Settings":
        origins = tuple(
            origin.strip()
            for origin in str(values.get("allowed_origins", ",".join(DEFAULT_ORIGINS))).split(",")
            if origin.strip()
        )
        lan_enabled = _as_bool(values.get("lan_enabled", False), "lan_enabled")
        settings = cls(
            database_path=Path(str(values.get("database_path", "data/pwtool.sqlite3"))),
            session_key=_decode_key(str(values["session_key"]), "session_key"),
            history_key=_decode_key(str(values["history_key"]), "history_key"),
            allowed_origins=origins,
            lan_enabled=lan_enabled,
            cookie_secure=_as_bool(values.get("cookie_secure", lan_enabled), "cookie_secure"),
            cookie_samesite=str(values.get("cookie_samesite", "strict" if lan_enabled else "lax")).lower(),
        )
        settings.validate()
        return settings

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> "Settings":
        config_path = Path(path or os.environ.get("PWTOOL_CONFIG", ".pwtool.local.json"))
        try:
            values = json.loads(config_path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise RuntimeError(
                f"Configuration {config_path} is missing. Run the platform setup script first."
            ) from error
        if not isinstance(values, dict):
            raise RuntimeError("PW-Tool configuration must be a JSON object")
        return cls.from_mapping(values)

    def validate(self) -> None:
        if not self.allowed_origins:
            raise ValueError("At least one explicit allowed origin is required")
        if "*" in self.allowed_origins:
            raise ValueError("Wildcard CORS origins are forbidden")
        if self.cookie_samesite not in {"lax", "strict"}:
            raise ValueError("cookie_samesite must be lax or strict")
        for origin in self.allowed_origins:
            parsed = urlparse(origin)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("Allowed origins must be absolute http(s) origins")
            if parsed.path not in {"", "/"} or parsed.params or parsed.query or parsed.fragment:
                raise ValueError("Allowed origins must not contain a path, query, or fragment")
        if self.lan_enabled:
            if all(_is_local_origin(origin) for origin in self.allowed_origins):
                raise ValueError("LAN mode requires at least one explicit LAN origin")
            if not self.cookie_secure:
                raise ValueError("LAN mode requires cookie_secure=true behind TLS")
            if any(urlparse(origin).scheme != "https" for origin in self.allowed_origins):
                raise ValueError("LAN mode requires explicit HTTPS origins")

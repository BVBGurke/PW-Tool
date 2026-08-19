"""Explizite, lokale Konfiguration für den PW-Tool-LAN-Betrieb."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path


DEFAULT_ORIGINS = ("http://127.0.0.1:5173", "http://localhost:5173")


def _decode_key(value: str, label: str) -> bytes:
    try:
        decoded = base64.urlsafe_b64decode(value.encode("ascii"))
    except Exception as error:
        raise ValueError(f"{label} is not valid URL-safe base64") from error
    if len(decoded) != 32:
        raise ValueError(f"{label} must decode to exactly 32 bytes")
    return decoded


@dataclass(frozen=True)
class Settings:
    database_path: Path
    session_key: bytes
    history_key: bytes
    allowed_origins: tuple[str, ...]
    lan_enabled: bool

    @classmethod
    def from_mapping(cls, values: dict[str, object]) -> "Settings":
        origins = tuple(
            origin.strip()
            for origin in str(values.get("allowed_origins", ",".join(DEFAULT_ORIGINS))).split(",")
            if origin.strip()
        )
        settings = cls(
            database_path=Path(str(values.get("database_path", "data/pwtool.sqlite3"))),
            session_key=_decode_key(str(values["session_key"]), "session_key"),
            history_key=_decode_key(str(values["history_key"]), "history_key"),
            allowed_origins=origins,
            lan_enabled=bool(values.get("lan_enabled", False)),
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
        if self.lan_enabled and all("127.0.0.1" in origin or "localhost" in origin for origin in self.allowed_origins):
            raise ValueError("LAN mode requires at least one explicit LAN origin")

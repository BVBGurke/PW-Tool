"""Kleine SQLite-Datenzugriffsschicht ohne dynamische SQL-Strings."""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE COLLATE NOCASE,
  password_hash TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token_digest TEXT PRIMARY KEY, account_id INTEGER NOT NULL,
  expires_at TEXT NOT NULL, created_at TEXT NOT NULL,
  FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS history_entries (
  id INTEGER PRIMARY KEY, account_id INTEGER NOT NULL, nonce BLOB NOT NULL,
  ciphertext BLOB NOT NULL, charset TEXT NOT NULL, created_at TEXT NOT NULL,
  FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_sessions_account ON sessions(account_id);
CREATE INDEX IF NOT EXISTS idx_history_account ON history_entries(account_id, id DESC);
"""


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def create_account(self, username: str, password_hash: str) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO accounts(username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, datetime.now(timezone.utc).isoformat()),
            )
            return int(cursor.lastrowid)

    def account_by_username(self, username: str) -> sqlite3.Row | None:
        with self.connect() as connection:
            return connection.execute("SELECT * FROM accounts WHERE username = ?", (username,)).fetchone()

    def create_session(self, digest: str, account_id: int, expires_at: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO sessions(token_digest, account_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
                (digest, account_id, expires_at, datetime.now(timezone.utc).isoformat()),
            )

    def account_for_session(self, digest: str) -> sqlite3.Row | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
            return connection.execute(
                "SELECT accounts.* FROM sessions JOIN accounts ON accounts.id = sessions.account_id "
                "WHERE sessions.token_digest = ? AND sessions.expires_at > ?", (digest, now),
            ).fetchone()

    def delete_session(self, digest: str) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_digest = ?", (digest,))

    def add_history(self, account_id: int, nonce: bytes, ciphertext: bytes, charset: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO history_entries(account_id, nonce, ciphertext, charset, created_at) VALUES (?, ?, ?, ?, ?)",
                (account_id, nonce, ciphertext, charset, datetime.now(timezone.utc).isoformat()),
            )

    def history_for_account(self, account_id: int) -> list[sqlite3.Row]:
        with self.connect() as connection:
            return connection.execute(
                "SELECT * FROM history_entries WHERE account_id = ? ORDER BY id DESC LIMIT 100", (account_id,)
            ).fetchall()

    def delete_history_entry(self, account_id: int, entry_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM history_entries WHERE id = ? AND account_id = ?", (entry_id, account_id))
            return cursor.rowcount == 1

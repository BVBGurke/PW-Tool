"""Erzeugt einmalig eine nicht eingecheckte PW-Tool-Laufzeitkonfiguration."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import secrets


def key() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=".pwtool.local.json")
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    path = Path(arguments.path)
    if path.exists() and not arguments.force:
        print(f"Configuration already exists: {path}")
        return
    path.write_text(json.dumps({"database_path": "data/pwtool.sqlite3", "session_key": key(), "history_key": key(), "allowed_origins": "http://127.0.0.1:5173,http://localhost:5173", "lan_enabled": False}, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)
    print(f"Created local configuration: {path}")


if __name__ == "__main__":
    main()

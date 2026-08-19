"""Prüft vor dem Serverstart, ob Bindungsmodus und lokale Konfiguration zusammenpassen."""

from __future__ import annotations

import argparse

from app.core.config import Settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--bind", choices=("local", "lan"), required=True)
    arguments = parser.parse_args()
    settings = Settings.from_file(arguments.config)
    if arguments.bind == "lan" and not settings.lan_enabled:
        raise SystemExit("LAN bind requested but lan_enabled is false in local configuration")
    if arguments.bind == "lan" and not settings.cookie_secure:
        raise SystemExit("LAN bind requires cookie_secure=true and HTTPS origins behind TLS")


if __name__ == "__main__":
    main()

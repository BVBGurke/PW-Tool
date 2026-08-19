"""Uvicorn-Entrypoint für den PW-Tool-Backend-Server."""

from pwtool.app import create_app
from pwtool.config import Settings

app = create_app(Settings.from_file())

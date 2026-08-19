"""Kompatibler Uvicorn-Einstiegspunkt für die geschichtete PW-Tool-API."""

from app.core.config import Settings
from app.main import create_app


app = create_app(Settings.from_file())

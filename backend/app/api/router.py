"""Zusammenführung der stabilen, versionierten lokalen API."""

from fastapi import APIRouter

from .routes import auth, health, history, passwords, security


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(passwords.router)
api_router.include_router(history.router)
api_router.include_router(security.router)

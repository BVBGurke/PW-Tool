"""FastAPI-App-Fabrik mit expliziten Schichten und Sicherheitsmiddleware."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .core.config import Settings
from .core.exceptions import DomainError, domain_error_handler, unexpected_error_handler, validation_error_handler
from .middleware.origin_check import OriginCheckMiddleware
from .middleware.rate_limit import MemoryRateLimiter
from .middleware.request_id import RequestIdMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
from .repositories.accounts import AccountRepository
from .repositories.database import Database
from .repositories.history import HistoryRepository
from .repositories.sessions import SessionRepository
from .services.auth import AuthService
from .services.capability import CapabilityService
from .services.hash_demo import HashDemoService
from .services.history import HistoryService
from .services.passwords import PasswordService
from .services.registry import ServiceRegistry


def create_app(settings: Settings) -> FastAPI:
    database = Database(settings.database_path)
    database.initialize()
    accounts = AccountRepository(database)
    sessions = SessionRepository(database)
    history = HistoryRepository(database)

    app = FastAPI(title="PW-Tool Local API", version="1.0.0", docs_url="/api/docs", redoc_url=None)
    app.state.settings = settings
    app.state.rate_limiter = MemoryRateLimiter()
    app.state.services = ServiceRegistry(
        auth=AuthService(accounts, sessions, settings),
        passwords=PasswordService(history, settings.history_key),
        history=HistoryService(history, settings.history_key),
        hash_demo=HashDemoService(),
        capability=CapabilityService(),
    )
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
    app.add_middleware(OriginCheckMiddleware, allowed_origins=settings.allowed_origins)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )
    app.include_router(api_router)
    return app

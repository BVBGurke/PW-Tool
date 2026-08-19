"""Explizite FastAPI-Abhängigkeiten für Services, Sitzungen und Limits."""

from __future__ import annotations

from fastapi import Cookie, Depends, Request

from ..core.exceptions import RateLimitError
from ..middleware.rate_limit import MemoryRateLimiter
from ..models.records import AccountRecord
from ..services.registry import ServiceRegistry


COOKIE_NAME = "pwtool_session"


def get_services(request: Request) -> ServiceRegistry:
    return request.app.state.services  # type: ignore[no-any-return]


def get_limiter(request: Request) -> MemoryRateLimiter:
    return request.app.state.rate_limiter  # type: ignore[no-any-return]


def get_current_account(
    services: ServiceRegistry = Depends(get_services),
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> AccountRecord:
    return services.auth.account_for_token(session_token)


def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def enforce_limit(limiter: MemoryRateLimiter, key: str, limit: int, seconds: float) -> None:
    if not limiter.allow(key, limit, seconds):
        raise RateLimitError()

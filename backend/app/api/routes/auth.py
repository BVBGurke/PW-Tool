"""Konto- und Sitzungsschnittstellen."""

from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, Request, Response, status

from ...core.config import Settings
from ...models.records import AccountRecord
from ...schemas.auth import AccountOutput, CredentialsInput, SessionOutput
from ...services.registry import ServiceRegistry
from ..dependencies import COOKIE_NAME, client_key, enforce_limit, get_current_account, get_limiter, get_services
from ...middleware.rate_limit import MemoryRateLimiter


router = APIRouter(prefix="/auth", tags=["authentication"])


def _account_output(account: AccountRecord) -> AccountOutput:
    return AccountOutput(id=account.id, username=account.username)


def _set_session(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
        max_age=12 * 60 * 60,
        path="/",
    )


@router.post("/register", response_model=SessionOutput, status_code=status.HTTP_201_CREATED)
def register(
    credentials: CredentialsInput,
    request: Request,
    response: Response,
    services: ServiceRegistry = Depends(get_services),
    limiter: MemoryRateLimiter = Depends(get_limiter),
) -> SessionOutput:
    enforce_limit(limiter, f"register:{client_key(request)}", 5, 60)
    account, token = services.auth.register(credentials.username, credentials.password)
    _set_session(response, token, services.auth.settings)
    return SessionOutput(account=_account_output(account))


@router.post("/login", response_model=SessionOutput)
def login(
    credentials: CredentialsInput,
    request: Request,
    response: Response,
    services: ServiceRegistry = Depends(get_services),
    limiter: MemoryRateLimiter = Depends(get_limiter),
) -> SessionOutput:
    enforce_limit(limiter, f"login:{client_key(request)}", 8, 60)
    account, token = services.auth.login(credentials.username, credentials.password)
    _set_session(response, token, services.auth.settings)
    return SessionOutput(account=_account_output(account))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    services: ServiceRegistry = Depends(get_services),
) -> Response:
    services.auth.logout(session_token)
    response.delete_cookie(COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=SessionOutput)
def me(account: AccountRecord = Depends(get_current_account)) -> SessionOutput:
    return SessionOutput(account=_account_output(account))

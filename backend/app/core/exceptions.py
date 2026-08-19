"""Domänenfehler und zentral redigierte API-Fehlerantworten."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR


logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Ein kontrollierter fachlicher Fehler ohne interne Details."""

    def __init__(self, status_code: int, code: str, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail


class AuthenticationError(DomainError):
    def __init__(self) -> None:
        super().__init__(401, "authentication_required", "Anmeldung erforderlich oder Sitzung abgelaufen.")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__(401, "invalid_credentials", "Benutzername oder Kennwort ist nicht gültig.")


class AccountUnavailableError(DomainError):
    def __init__(self) -> None:
        super().__init__(409, "account_unavailable", "Dieses Konto kann nicht eingerichtet werden.")


class NotFoundError(DomainError):
    def __init__(self, detail: str = "Der angeforderte Eintrag ist nicht vorhanden.") -> None:
        super().__init__(404, "not_found", detail)


class RateLimitError(DomainError):
    def __init__(self) -> None:
        super().__init__(429, "rate_limited", "Zu viele Anfragen. Bitte später erneut versuchen.")


class OriginRejectedError(DomainError):
    def __init__(self) -> None:
        super().__init__(403, "origin_rejected", "Diese Herkunft ist für zustandsändernde Anfragen nicht zugelassen.")


def problem_body(request: Request, status_code: int, code: str, detail: str, errors: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "type": f"https://pw-tool.local/problems/{code}",
        "title": code.replace("_", " "),
        "status": status_code,
        "detail": detail,
        "request_id": getattr(request.state, "request_id", "unknown"),
    }
    if errors:
        body["errors"] = errors
    return body


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        problem_body(request, exc.status_code, exc.code, exc.detail),
        status_code=exc.status_code,
        media_type="application/problem+json",
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    safe_errors = [
        {"location": list(error.get("loc", ())), "message": str(error.get("msg", "invalid input"))}
        for error in exc.errors()
    ]
    return JSONResponse(
        problem_body(request, HTTP_422_UNPROCESSABLE_CONTENT, "validation_failed", "Eingaben prüfen.", safe_errors),
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        media_type="application/problem+json",
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unbehandelter API-Fehler request_id=%s", getattr(request.state, "request_id", "unknown"))
    return JSONResponse(
        problem_body(request, HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", "Ein interner Fehler ist aufgetreten."),
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        media_type="application/problem+json",
    )

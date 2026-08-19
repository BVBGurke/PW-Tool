"""Zusätzliche Origin-Prüfung für alle Browser-Zustandsänderungen."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..core.exceptions import problem_body


class OriginCheckMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_origins: tuple[str, ...]) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.allowed_origins = set(allowed_origins)

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        sensitive = request.method in {"POST", "PUT", "PATCH", "DELETE"}
        if sensitive and request.url.path.startswith("/api/"):
            origin = request.headers.get("origin")
            if origin and origin not in self.allowed_origins:
                return JSONResponse(
                    problem_body(request, 403, "origin_rejected", "Diese Herkunft ist nicht zugelassen."),
                    status_code=403,
                    media_type="application/problem+json",
                )
        return await call_next(request)

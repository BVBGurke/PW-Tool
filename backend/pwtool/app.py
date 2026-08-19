"""FastAPI-Anwendung für den lokalen und bewusst konfigurierten LAN-Betrieb."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib
import hmac
import os
import re
from time import monotonic, perf_counter
from typing import Deque

from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import Settings
from .core.passwords import COMPLETE, NORMAL, generate_batch, security_summary, validate_request
from .db import Database
from .security import (
    decrypt_history_value,
    encrypt_history_value,
    expiry_timestamp,
    hash_account_password,
    new_session_token,
    session_digest,
    verify_account_password,
)

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,64}$")
COOKIE_NAME = "pwtool_session"


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=12, max_length=1024)


class GenerationInput(BaseModel):
    length: int = Field(default=64, ge=16, le=256)
    count: int = Field(default=1, ge=1, le=10_000)
    charset: str = Field(default=COMPLETE, pattern="^(normal|complete)$")
    save_history: bool = False


class HashDemoInput(BaseModel):
    length: int = Field(default=32, ge=16, le=256)
    charset: str = Field(default=COMPLETE, pattern="^(normal|complete)$")


class MemoryRateLimiter:
    """Kleine prozesslokale Begrenzung für Login- und API-Spitzen."""

    def __init__(self) -> None:
        self._events: dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: float) -> bool:
        now = monotonic()
        events = self._events[key]
        while events and now - events[0] > window_seconds:
            events.popleft()
        if len(events) >= limit:
            return False
        events.append(now)
        return True


def _account_payload(account: object) -> dict[str, object]:
    return {"id": int(account["id"]), "username": str(account["username"])}  # type: ignore[index]


def create_app(settings: Settings) -> FastAPI:
    database = Database(settings.database_path)
    database.initialize()
    limiter = MemoryRateLimiter()
    app = FastAPI(title="PW-Tool LAN API", version="0.2.0b1", docs_url="/api/docs")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )

    def request_key(request: Request) -> str:
        return request.client.host if request.client else "unknown"

    def enforce_origin(request: Request) -> None:
        origin = request.headers.get("origin")
        if origin and origin not in settings.allowed_origins:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="origin not allowed")

    def current_account(session_token: str | None = Cookie(default=None, alias=COOKIE_NAME)) -> object:
        if not session_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
        account = database.account_for_session(session_digest(session_token, settings.session_key))
        if account is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="session expired")
        return account

    def set_session(response: Response, account_id: int) -> None:
        token = new_session_token()
        database.create_session(session_digest(token, settings.session_key), account_id, expiry_timestamp())
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=12 * 60 * 60,
            path="/",
        )

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "lan_enabled": settings.lan_enabled, "allowed_origins": settings.allowed_origins}

    @app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
    def register(credentials: Credentials, request: Request, response: Response) -> dict[str, object]:
        enforce_origin(request)
        if not limiter.allow(f"register:{request_key(request)}", 5, 60):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="try again later")
        username = credentials.username.strip()
        if not USERNAME_PATTERN.fullmatch(username):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid username")
        try:
            account_id = database.create_account(username, hash_account_password(credentials.password))
        except Exception as error:
            if "UNIQUE" in str(error).upper():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username unavailable") from error
            raise
        set_session(response, account_id)
        return {"account": {"id": account_id, "username": username}}

    @app.post("/api/auth/login")
    def login(credentials: Credentials, request: Request, response: Response) -> dict[str, object]:
        enforce_origin(request)
        if not limiter.allow(f"login:{request_key(request)}", 8, 60):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="try again later")
        account = database.account_by_username(credentials.username.strip())
        if account is None or not verify_account_password(credentials.password, str(account["password_hash"])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
        set_session(response, int(account["id"]))
        return {"account": _account_payload(account)}

    @app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
    def logout(request: Request, response: Response, session_token: str | None = Cookie(default=None, alias=COOKIE_NAME)) -> Response:
        enforce_origin(request)
        if session_token:
            database.delete_session(session_digest(session_token, settings.session_key))
        response.delete_cookie(COOKIE_NAME, path="/")
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    @app.get("/api/auth/me")
    def me(account: object = Depends(current_account)) -> dict[str, object]:
        return {"account": _account_payload(account)}

    @app.post("/api/passwords/generate")
    def generate(payload: GenerationInput, request: Request, account: object = Depends(current_account)) -> dict[str, object]:
        enforce_origin(request)
        if not limiter.allow(f"generate:{int(account['id'])}", 60, 60):  # type: ignore[index]
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="try again later")
        try:
            validate_request(payload.length, payload.count, payload.charset)
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
        passwords = generate_batch(payload.length, payload.count, payload.charset)
        if payload.save_history:
            for password in passwords:
                nonce, ciphertext = encrypt_history_value(password, settings.history_key, int(account["id"]))  # type: ignore[index]
                database.add_history(int(account["id"]), nonce, ciphertext, payload.charset)  # type: ignore[index]
        return {"passwords": passwords, "security": security_summary(passwords, payload.charset), "saved": payload.save_history}

    @app.get("/api/history")
    def history(account: object = Depends(current_account)) -> dict[str, object]:
        values: list[dict[str, object]] = []
        for row in database.history_for_account(int(account["id"])):  # type: ignore[index]
            values.append(
                {
                    "id": int(row["id"]),
                    "password": decrypt_history_value(row["nonce"], row["ciphertext"], settings.history_key, int(account["id"])),  # type: ignore[index]
                    "charset": str(row["charset"]),
                    "created_at": str(row["created_at"]),
                }
            )
        return {"entries": values}

    @app.delete("/api/history/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_history(entry_id: int, request: Request, account: object = Depends(current_account)) -> Response:
        enforce_origin(request)
        if not database.delete_history_entry(int(account["id"]), entry_id):  # type: ignore[index]
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="entry not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.post("/api/security/hash-demo")
    def hash_demo(payload: HashDemoInput, request: Request, account: object = Depends(current_account)) -> dict[str, object]:
        """Zeigt nur KDF-Metadaten; keine fremden Hashes oder Rateversuche."""
        enforce_origin(request)
        validate_request(payload.length, 1, payload.charset)
        demo_value = generate_batch(payload.length, 1, payload.charset)[0]
        salt = os.urandom(16)
        start = perf_counter()
        derived = hashlib.scrypt(demo_value.encode(), salt=salt, n=2**14, r=8, p=1, maxmem=64 * 1024 * 1024, dklen=32)
        verified = hmac.compare_digest(
            hashlib.scrypt(demo_value.encode(), salt=salt, n=2**14, r=8, p=1, maxmem=64 * 1024 * 1024, dklen=32),
            derived,
        )
        duration_ms = (perf_counter() - start) * 1000
        return {"algorithm": "scrypt", "n": 16384, "r": 8, "p": 1, "salt_bytes": 16, "output_bytes": 32, "duration_ms": round(duration_ms, 1), "verified": verified, "notice": "self-generated local demo only"}

    return app

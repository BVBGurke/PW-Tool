"""Konten und serverseitige Sitzungen ohne HTTP-Kopplung."""

from __future__ import annotations

import re
import sqlite3

from ..core.config import Settings
from ..core.exceptions import AccountUnavailableError, AuthenticationError, InvalidCredentialsError
from ..models.records import AccountRecord
from ..repositories.accounts import AccountRepository
from ..repositories.sessions import SessionRepository
from ..security.passwords import hash_account_password, verify_account_password
from ..security.sessions import expiry_timestamp, new_session_token, session_digest


USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,64}$")
_DUMMY_PASSWORD_HASH = hash_account_password("pwtool-invalid-login-placeholder")


class AuthService:
    def __init__(self, accounts: AccountRepository, sessions: SessionRepository, settings: Settings) -> None:
        self.accounts = accounts
        self.sessions = sessions
        self.settings = settings

    def register(self, username: str, password: str) -> tuple[AccountRecord, str]:
        normalized_username = username.strip()
        if not USERNAME_PATTERN.fullmatch(normalized_username):
            raise AccountUnavailableError()
        password_hash = hash_account_password(password)
        try:
            account = self.accounts.create(normalized_username, password_hash)
        except sqlite3.IntegrityError as error:
            raise AccountUnavailableError() from error
        return account, self._create_session(account.id)

    def login(self, username: str, password: str) -> tuple[AccountRecord, str]:
        account = self.accounts.by_username(username.strip())
        candidate_hash = account.password_hash if account else _DUMMY_PASSWORD_HASH
        if not verify_account_password(password, candidate_hash) or account is None:
            raise InvalidCredentialsError()
        return account, self._create_session(account.id)

    def account_for_token(self, token: str | None) -> AccountRecord:
        if not token:
            raise AuthenticationError()
        account = self.sessions.account_for_digest(session_digest(token, self.settings.session_key))
        if account is None:
            raise AuthenticationError()
        return account

    def logout(self, token: str | None) -> None:
        if token:
            self.sessions.delete(session_digest(token, self.settings.session_key))

    def _create_session(self, account_id: int) -> str:
        token = new_session_token()
        self.sessions.create(session_digest(token, self.settings.session_key), account_id, expiry_timestamp())
        return token

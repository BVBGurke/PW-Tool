"""Sichere Passwortableitung aus kryptografischem Entropiematerial.

Die Implementierung nutzt HMAC-SHA-512-Blöcke und Rejection Sampling. Dadurch
hängt jedes Zeichen tatsächlich vom übergebenen Entropiematerial ab, es entstehen
keine großen temporären Zeichenpools und es gibt keinen Modulo-Bias.
"""

from __future__ import annotations

import hashlib
import hmac
import string
from enum import Enum


class CharacterSet(Enum):
    """Verfügbare Zeichensätze für Passwörter."""

    NORMAL = "normal"
    COMPLETE = "complete"


class PasswordGenerator:
    """Leitet Passwörter lokal und effizient aus einem Entropieseed ab."""

    CHARS_NORMAL = string.ascii_letters + string.digits
    CHARS_COMPLETE = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}"
    _BLOCK_DOMAIN = b"PW-Tool PasswordBlock v1"
    _BATCH_DOMAIN = b"PW-Tool BatchEntropy v1"

    @staticmethod
    def validate_length(length: int) -> bool:
        """Prüft die unterstützte Passwortlänge von 8 bis 256 Zeichen."""
        return 8 <= length <= 256

    @staticmethod
    def get_character_set(charset: CharacterSet) -> str:
        """Gibt die Zeichen des gewählten Zeichensatzes zurück."""
        if charset == CharacterSet.COMPLETE:
            return PasswordGenerator.CHARS_COMPLETE
        return PasswordGenerator.CHARS_NORMAL

    @staticmethod
    def generate(
        entropy: bytes,
        length: int,
        charset: CharacterSet = CharacterSet.NORMAL,
    ) -> str:
        """Leitet ein Passwort per HMAC-SHA-512 und Rejection Sampling ab.

        Das Verfahren vermeidet die Modulo-Verzerrung von ``byte % alphabet``.
        Entropie wird vollständig in der HMAC-Schlüsselposition verwendet, daher
        wirkt sich eine Änderung im Systemmix auf das resultierende Passwort aus.
        """
        if not PasswordGenerator.validate_length(length):
            raise ValueError(f"Length must be 8-256, got {length}")
        if not entropy:
            raise ValueError("Entropy must not be empty")

        characters = PasswordGenerator.get_character_set(charset)
        acceptance_limit = 256 - (256 % len(characters))
        password = []
        block_counter = 0

        while len(password) < length:
            block = hmac.new(
                entropy,
                PasswordGenerator._BLOCK_DOMAIN + block_counter.to_bytes(8, "big"),
                hashlib.sha512,
            ).digest()
            block_counter += 1

            for value in block:
                if value >= acceptance_limit:
                    continue
                password.append(characters[value % len(characters)])
                if len(password) == length:
                    break

        return "".join(password)

    @staticmethod
    def generate_batch(
        entropy: bytes,
        count: int,
        length: int,
        charset: CharacterSet = CharacterSet.NORMAL,
    ) -> list[str]:
        """Leitet für jeden Batch-Eintrag einen getrennten Entropieseed ab."""
        if count < 1:
            raise ValueError("Count must be >= 1")

        passwords = []
        for index in range(count):
            unique_entropy = hashlib.sha512(
                PasswordGenerator._BATCH_DOMAIN
                + entropy
                + index.to_bytes(8, "big")
            ).digest()
            passwords.append(PasswordGenerator.generate(unique_entropy, length, charset))

        return passwords


def parse_charset_input(choice: str) -> CharacterSet:
    """Parst die CLI-Auswahl für einen Zeichensatz."""
    choice_lower = choice.lower().strip()
    if choice_lower in ("1", "normal"):
        return CharacterSet.NORMAL
    if choice_lower in ("2", "complete"):
        return CharacterSet.COMPLETE
    raise ValueError(f"Invalid character set choice: {choice}")

"""Sichere Passwortableitung und direkte OS-CSPRNG-Policy-Erzeugung.

Die sichtbaren Textual-Formate verwenden eine gemeinsame, auditierbare Policy:
OS-CSPRNG, Rejection Sampling, garantierte Zeichenklassen und einen
CSPRNG-basierten Fisher-Yates-Shuffle. Die historisch deterministische
HMAC-Ableitung bleibt für interne Kompatibilitätstests erhalten, ist aber kein
sichtbarer interaktiver Pfad mehr.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import string
from enum import Enum
from typing import Callable


class CharacterSet(Enum):
    """Verfügbare Zeichenauswahlen für sichere Passwort-Policies."""

    NORMAL = "normal"
    COMPLETE = "complete"
    MAXIMUM = "maximum"  # Interne Rückwärtskompatibilitätsbezeichnung für COMPLETE.


MIN_PASSWORD_LENGTH = 16
MAX_PASSWORD_LENGTH = 256
RandomBytes = Callable[[int], bytes]


class PasswordGenerator:
    """Erzeugt lokale Passwörter aus sicheren, nachvollziehbaren Zufallspfaden."""

    CHARS_NORMAL = string.ascii_letters + string.digits
    CHARS_COMPLETE = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}"
    _LOWERCASE = string.ascii_lowercase
    _UPPERCASE = string.ascii_uppercase
    _DIGITS = string.digits
    _SPECIALS = "!@#$%^&*()-_=+[]{}"
    _BLOCK_DOMAIN = b"PW-Tool PasswordBlock v1"
    _BATCH_DOMAIN = b"PW-Tool BatchEntropy v1"

    @staticmethod
    def validate_length(length: int) -> bool:
        """Prüft die sicherheitsorientierte Länge von 16 bis 256 Zeichen."""
        return MIN_PASSWORD_LENGTH <= length <= MAX_PASSWORD_LENGTH

    @staticmethod
    def get_character_set(charset: CharacterSet) -> str:
        """Gibt das zulässige Alphabet der gewählten Policy zurück."""
        if charset in (CharacterSet.COMPLETE, CharacterSet.MAXIMUM):
            return PasswordGenerator.CHARS_COMPLETE
        return PasswordGenerator.CHARS_NORMAL

    @staticmethod
    def _random_block(random_bytes: RandomBytes, size: int) -> bytes:
        """Liest genau ``size`` Bytes aus einer testbar austauschbaren CSPRNG-Quelle."""
        block = random_bytes(size)
        if len(block) != size:
            raise ValueError("Random byte source returned an unexpected byte count")
        return block

    @classmethod
    def _uniform_index(cls, alphabet_size: int, random_bytes: RandomBytes) -> int:
        """Wählt einen Index ohne Modulo-Bias mittels Rejection Sampling."""
        if alphabet_size < 1 or alphabet_size > 256:
            raise ValueError("alphabet_size must be in range 1..256")

        acceptance_limit = 256 - (256 % alphabet_size)
        while True:
            for value in cls._random_block(random_bytes, 64):
                if value < acceptance_limit:
                    return value % alphabet_size

    @classmethod
    def _uniform_characters(
        cls,
        alphabet: str,
        count: int,
        random_bytes: RandomBytes,
    ) -> list[str]:
        """Zieht ``count`` Zeichen bias-frei aus einem Alphabet."""
        if not alphabet:
            raise ValueError("alphabet must not be empty")
        return [alphabet[cls._uniform_index(len(alphabet), random_bytes)] for _ in range(count)]

    @classmethod
    def _fisher_yates_shuffle(cls, values: list[str], random_bytes: RandomBytes) -> None:
        """Mischt Werte in-place mit ausschließlich bias-freien CSPRNG-Indizes."""
        for index in range(len(values) - 1, 0, -1):
            swap_index = cls._uniform_index(index + 1, random_bytes)
            values[index], values[swap_index] = values[swap_index], values[index]

    @classmethod
    def _required_groups(cls, charset: CharacterSet) -> tuple[str, ...]:
        """Gibt die Zeichenklassen zurück, die pro Passwort garantiert werden."""
        base_groups = (cls._LOWERCASE, cls._UPPERCASE, cls._DIGITS)
        if charset in (CharacterSet.COMPLETE, CharacterSet.MAXIMUM):
            return (*base_groups, cls._SPECIALS)
        return base_groups

    @classmethod
    def generate_policy(
        cls,
        length: int,
        charset: CharacterSet = CharacterSet.COMPLETE,
        *,
        random_bytes: RandomBytes = os.urandom,
    ) -> str:
        """Erzeugt ein Passwort direkt aus dem OS-CSPRNG nach einer Klassen-Policy.

        Für `normal` sind Kleinbuchstabe, Großbuchstabe und Ziffer garantiert.
        Für `complete` kommt ein Sonderzeichen hinzu. Alle restlichen Zeichen
        werden aus dem vollständigen gewählten Alphabet gezogen und anschließend
        CSPRNG-basiert gemischt.
        """
        if not cls.validate_length(length):
            raise ValueError(
                f"Length must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH}, got {length}"
            )

        groups = cls._required_groups(charset)
        password = [cls._uniform_characters(group, 1, random_bytes)[0] for group in groups]
        alphabet = cls.get_character_set(charset)
        password.extend(cls._uniform_characters(alphabet, length - len(password), random_bytes))
        cls._fisher_yates_shuffle(password, random_bytes)
        return "".join(password)

    @classmethod
    def generate_policy_batch(
        cls,
        count: int,
        length: int,
        charset: CharacterSet = CharacterSet.COMPLETE,
        *,
        random_bytes: RandomBytes = os.urandom,
    ) -> list[str]:
        """Erzeugt einen Batch unabhängiger CSPRNG-Policy-Passwörter."""
        if count < 1:
            raise ValueError("Count must be >= 1")
        return [cls.generate_policy(length, charset, random_bytes=random_bytes) for _ in range(count)]

    @classmethod
    def generate_maximum(
        cls,
        length: int,
        *,
        random_bytes: RandomBytes = os.urandom,
    ) -> str:
        """Kompatibilitätswrapper für die vollständige CSPRNG-Policy."""
        return cls.generate_policy(length, CharacterSet.COMPLETE, random_bytes=random_bytes)

    @classmethod
    def generate_maximum_batch(
        cls,
        count: int,
        length: int,
        *,
        random_bytes: RandomBytes = os.urandom,
    ) -> list[str]:
        """Kompatibilitätswrapper für vollständige CSPRNG-Policy-Batches."""
        return cls.generate_policy_batch(count, length, CharacterSet.COMPLETE, random_bytes=random_bytes)

    @staticmethod
    def generate(
        entropy: bytes,
        length: int,
        charset: CharacterSet = CharacterSet.NORMAL,
    ) -> str:
        """Leitet für interne Kompatibilität per HMAC-SHA-512 ein Passwort ab."""
        if not PasswordGenerator.validate_length(length):
            raise ValueError(
                f"Length must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH}, got {length}"
            )
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
        """Leitet für interne Kompatibilität getrennte Werte aus einem Seed ab."""
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
    """Parst eine der zwei sichtbaren Zeichenauswahlen oder das Legacy-Profil."""
    choice_lower = choice.lower().strip()
    if choice_lower in ("1", "normal", "compatible"):
        return CharacterSet.NORMAL
    if choice_lower in ("2", "complete", "full"):
        return CharacterSet.COMPLETE
    if choice_lower in ("3", "maximum", "secure"):
        return CharacterSet.MAXIMUM
    raise ValueError(f"Invalid character set choice: {choice}")

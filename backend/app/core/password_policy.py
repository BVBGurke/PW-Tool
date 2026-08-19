"""Direkte, bias-freie OS-CSPRNG-Passworterzeugung."""

from __future__ import annotations

import math
import os
import string


MIN_LENGTH = 16
MAX_LENGTH = 256
MAX_COUNT = 10_000
NORMAL = "normal"
COMPLETE = "complete"
ALPHABETS = {
    NORMAL: string.ascii_letters + string.digits,
    COMPLETE: string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}",
}
GROUPS = {
    NORMAL: (string.ascii_lowercase, string.ascii_uppercase, string.digits),
    COMPLETE: (string.ascii_lowercase, string.ascii_uppercase, string.digits, "!@#$%^&*()-_=+[]{}"),
}


def validate_request(length: int, count: int, charset: str) -> None:
    if not MIN_LENGTH <= length <= MAX_LENGTH:
        raise ValueError(f"length must be {MIN_LENGTH}-{MAX_LENGTH}")
    if not 1 <= count <= MAX_COUNT:
        raise ValueError(f"count must be 1-{MAX_COUNT}")
    if charset not in ALPHABETS:
        raise ValueError("charset must be normal or complete")


def _index(size: int) -> int:
    limit = 256 - (256 % size)
    while True:
        for value in os.urandom(64):
            if value < limit:
                return value % size


def _shuffle(values: list[str]) -> None:
    for position in range(len(values) - 1, 0, -1):
        target = _index(position + 1)
        values[position], values[target] = values[target], values[position]


def generate_one(length: int, charset: str) -> str:
    validate_request(length, 1, charset)
    values = [group[_index(len(group))] for group in GROUPS[charset]]
    alphabet = ALPHABETS[charset]
    values.extend(alphabet[_index(len(alphabet))] for _ in range(length - len(values)))
    _shuffle(values)
    return "".join(values)


def generate_batch(length: int, count: int, charset: str) -> list[str]:
    validate_request(length, count, charset)
    return [generate_one(length, charset) for _ in range(count)]


def security_summary(passwords: list[str], charset: str) -> dict[str, object]:
    alphabet = ALPHABETS[charset]
    minimum_length = min(map(len, passwords))
    group_product = math.prod(len(group) for group in GROUPS[charset])
    guaranteed = len(GROUPS[charset])
    entropy_bits = math.log2(group_product) + (minimum_length - guaranteed) * math.log2(len(alphabet))
    return {
        "profile": charset,
        "minimum_length": minimum_length,
        "alphabet_size": len(alphabet),
        "conservative_entropy_bits": round(entropy_bits, 1),
        "all_distinct": len(set(passwords)) == len(passwords),
        "guaranteed_classes": guaranteed,
    }

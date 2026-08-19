from __future__ import annotations

import base64
import unittest

from pwtool.config import Settings


def key() -> str:
    return base64.urlsafe_b64encode(bytes(range(32))).decode("ascii")


class SettingsTests(unittest.TestCase):
    def test_lan_requires_explicit_non_local_origin(self) -> None:
        with self.assertRaisesRegex(ValueError, "LAN mode"):
            Settings.from_mapping({"session_key": key(), "history_key": key(), "lan_enabled": True})

    def test_wildcard_origin_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Wildcard"):
            Settings.from_mapping({"session_key": key(), "history_key": key(), "allowed_origins": "*"})

    def test_explicit_lan_origin_is_accepted(self) -> None:
        settings = Settings.from_mapping({"session_key": key(), "history_key": key(), "allowed_origins": "http://192.168.1.50:5173", "lan_enabled": True})
        self.assertTrue(settings.lan_enabled)

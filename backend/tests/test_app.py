from __future__ import annotations

import base64
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from pwtool.app import create_app
from pwtool.config import Settings


def _key() -> str:
    return base64.urlsafe_b64encode(bytes(range(32))).decode("ascii")


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.settings = Settings.from_mapping(
            {
                "database_path": str(Path(self.temporary.name) / "pwtool.sqlite3"),
                "session_key": _key(),
                "history_key": _key(),
                "allowed_origins": "http://127.0.0.1:5173",
                "lan_enabled": False,
            }
        )
        self.client = TestClient(create_app(self.settings))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def register(self) -> None:
        response = self.client.post("/api/auth/register", json={"username": "alice", "password": "correct-horse-battery-staple"})
        self.assertEqual(201, response.status_code)

    def test_account_generation_and_encrypted_history(self) -> None:
        self.register()
        generated = self.client.post("/api/passwords/generate", json={"length": 16, "count": 1, "charset": "complete", "save_history": True})
        self.assertEqual(200, generated.status_code)
        password = generated.json()["passwords"][0]
        self.assertEqual(16, len(password))
        self.assertTrue(any(not character.isalnum() for character in password))
        self.assertNotIn(password, str(generated.json()["security"]))

        history = self.client.get("/api/history")
        self.assertEqual(200, history.status_code)
        self.assertEqual(password, history.json()["entries"][0]["password"])
        with sqlite3.connect(self.settings.database_path) as connection:
            ciphertext = connection.execute("SELECT ciphertext FROM history_entries").fetchone()[0]
        self.assertNotIn(password.encode("utf-8"), ciphertext)
        self.assertEqual(204, self.client.delete(f"/api/history/{history.json()['entries'][0]['id']}").status_code)

    def test_logout_revokes_server_side_session(self) -> None:
        self.register()
        self.assertEqual(204, self.client.post("/api/auth/logout", json={}).status_code)
        self.assertEqual(401, self.client.get("/api/auth/me").status_code)

    def test_hash_demo_accepts_no_foreign_hashes_or_candidates(self) -> None:
        self.register()
        response = self.client.post("/api/security/hash-demo", json={"length": 16, "charset": "normal"})
        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual("scrypt", body["algorithm"])
        self.assertTrue(body["verified"])
        self.assertNotIn("password", body)
        self.assertNotIn("hash", body)

    def test_cross_origin_state_change_is_rejected(self) -> None:
        response = self.client.post(
            "/api/auth/register",
            headers={"Origin": "http://untrusted.invalid"},
            json={"username": "alice", "password": "correct-horse-battery-staple"},
        )
        self.assertEqual(403, response.status_code)


if __name__ == "__main__":
    unittest.main()

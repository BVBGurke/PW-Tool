"""Unit-Tests für die lokale Systemdatei-Mischung von PW-Tool."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from password_engine import CharacterSet, PasswordGenerator
from system_mix import (
    SystemMixStatus,
    candidate_paths,
    collect_system_mix,
    mix_entropy,
)


class SystemMixTests(unittest.TestCase):
    def test_supported_platform_allowlists_have_five_fixed_candidates(self) -> None:
        for platform_id in ("macos", "windows", "linux", "android"):
            candidates = candidate_paths(platform_id)
            self.assertEqual(5, len(candidates))
            self.assertTrue(all(stable_id for stable_id, _ in candidates))

    def test_three_readable_sources_create_complete_mix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidates = []
            for index, value in enumerate((b"alpha", b"bravo", b"charlie")):
                path = root / f"source-{index}.bin"
                path.write_bytes(value)
                candidates.append((f"test-{index}", path))

            result = collect_system_mix(platform_id="test", candidates=candidates)

        self.assertEqual(SystemMixStatus.COMPLETE, result.status)
        self.assertEqual(3, result.source_count)
        self.assertIsNotNone(result.aggregate_digest)
        self.assertEqual(64, len(result.aggregate_digest or b""))

    def test_candidate_order_changes_aggregate_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.bin"
            second = root / "second.bin"
            third = root / "third.bin"
            first.write_bytes(b"one")
            second.write_bytes(b"two")
            third.write_bytes(b"three")
            forward = collect_system_mix(
                platform_id="test",
                candidates=(("first", first), ("second", second), ("third", third)),
            )
            reversed_result = collect_system_mix(
                platform_id="test",
                candidates=(("third", third), ("second", second), ("first", first)),
            )

        self.assertNotEqual(forward.aggregate_digest, reversed_result.aggregate_digest)

    def test_incomplete_sources_do_not_return_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.bin"
            path.write_bytes(b"only one")
            result = collect_system_mix(
                platform_id="test",
                candidates=(("source", path), ("missing", path.with_name("missing"))),
            )

        self.assertEqual(SystemMixStatus.PARTIAL, result.status)
        self.assertEqual(1, result.source_count)
        self.assertIsNone(result.aggregate_digest)

    def test_hmac_mix_changes_entropy_only_for_complete_source(self) -> None:
        base_entropy = bytes(range(32))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidates = []
            for index, value in enumerate((b"alpha", b"bravo", b"charlie")):
                path = root / f"source-{index}.bin"
                path.write_bytes(value)
                candidates.append((f"test-{index}", path))
            complete = collect_system_mix(platform_id="test", candidates=candidates)

        mixed = mix_entropy(base_entropy, complete)
        partial = collect_system_mix(enabled=False)

        self.assertEqual(64, len(mixed))
        self.assertNotEqual(base_entropy, mixed)
        self.assertEqual(base_entropy, mix_entropy(base_entropy, partial))

    def test_password_derivation_is_deterministic_and_respects_charset(self) -> None:
        entropy = b"deterministic test entropy" * 4
        first = PasswordGenerator.generate(entropy, 64, CharacterSet.COMPLETE)
        second = PasswordGenerator.generate(entropy, 64, CharacterSet.COMPLETE)
        changed = PasswordGenerator.generate(entropy + b"x", 64, CharacterSet.COMPLETE)

        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertTrue(all(character in PasswordGenerator.CHARS_COMPLETE for character in first))


if __name__ == "__main__":
    unittest.main(verbosity=2)

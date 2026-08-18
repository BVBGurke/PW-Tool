from __future__ import annotations

import unittest

from backends.base import GenerationRequest, MAX_BATCH_COUNT
from password_engine import CharacterSet


class BatchLimitTests(unittest.TestCase):
    def test_maximum_beta_batch_is_accepted(self) -> None:
        request = GenerationRequest(
            password_count=MAX_BATCH_COUNT,
            password_length=8,
            charset=CharacterSet.NORMAL,
            iterations=1,
            system_mix_enabled=False,
        )
        self.assertEqual(MAX_BATCH_COUNT, request.password_count)

    def test_batch_above_beta_limit_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "1..10000"):
            GenerationRequest(
                password_count=MAX_BATCH_COUNT + 1,
                password_length=8,
                charset=CharacterSet.NORMAL,
                iterations=1,
                system_mix_enabled=False,
            )


if __name__ == "__main__":
    unittest.main()

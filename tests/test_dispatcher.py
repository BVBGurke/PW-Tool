from __future__ import annotations

from dataclasses import dataclass
import unittest

from backends.base import BackendKind, GenerationRequest, GenerationResult
from dispatcher import BackendDispatcher, BackendPreference
from password_engine import CharacterSet
from system_mix import SystemMixResult


@dataclass
class FakeBackend:
    kind: BackendKind
    available: bool

    def is_available(self) -> bool:
        return self.available

    def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self.available:
            raise RuntimeError("unavailable")
        return GenerationResult([], self.kind, SystemMixResult.disabled())


class DispatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = GenerationRequest(
            password_count=128,
            password_length=24,
            charset=CharacterSet.COMPLETE,
            iterations=1,
            system_mix_enabled=False,
        )

    def test_all_visible_profiles_use_cpu_when_cuda_is_unavailable(self) -> None:
        dispatcher = BackendDispatcher(
            cpu_backend=FakeBackend(BackendKind.CPU, True),
            cuda_backend=FakeBackend(BackendKind.CUDA, False),
        )

        decision = dispatcher.decide(self.request, BackendPreference.GPU_FIRST)

        self.assertEqual(BackendKind.CPU, decision.backend)
        self.assertIn("direct OS-CSPRNG", decision.reason)
        self.assertIsNone(decision.calibration_cpu_seconds)
        self.assertIsNone(decision.calibration_cuda_seconds)

    def test_all_visible_profiles_use_cpu_even_when_cuda_is_available(self) -> None:
        dispatcher = BackendDispatcher(
            cpu_backend=FakeBackend(BackendKind.CPU, True),
            cuda_backend=FakeBackend(BackendKind.CUDA, True),
        )

        decision = dispatcher.decide(self.request, BackendPreference.GPU_FIRST)

        self.assertEqual(BackendKind.CPU, decision.backend)
        self.assertIn("direct OS-CSPRNG", decision.reason)

    def test_legacy_preference_does_not_change_visible_randomness_path(self) -> None:
        dispatcher = BackendDispatcher(
            cpu_backend=FakeBackend(BackendKind.CPU, True),
            cuda_backend=FakeBackend(BackendKind.CUDA, True),
        )

        decision = dispatcher.decide(self.request, BackendPreference.CPU_ONLY)

        self.assertEqual(BackendKind.CPU, decision.backend)
        self.assertIn("direct OS-CSPRNG", decision.reason)


if __name__ == "__main__":
    unittest.main()

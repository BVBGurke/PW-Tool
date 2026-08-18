from __future__ import annotations

from dataclasses import dataclass
import time
import unittest

from backends.base import BackendKind, GenerationRequest, GenerationResult
from dispatcher import BackendDispatcher, BackendPreference
from password_engine import CharacterSet
from system_mix import SystemMixResult


@dataclass
class FakeBackend:
    kind: BackendKind
    available: bool
    delay_seconds: float = 0.0

    def is_available(self) -> bool:
        return self.available

    def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self.available:
            raise RuntimeError("unavailable")
        time.sleep(self.delay_seconds)
        return GenerationResult([], self.kind, SystemMixResult.disabled())


class DispatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = GenerationRequest(
            password_count=128,
            password_length=24,
            charset=CharacterSet.NORMAL,
            iterations=1,
            system_mix_enabled=False,
        )

    def test_unavailable_cuda_uses_cpu(self) -> None:
        dispatcher = BackendDispatcher(
            cpu_backend=FakeBackend(BackendKind.CPU, True),
            cuda_backend=FakeBackend(BackendKind.CUDA, False),
        )

        decision = dispatcher.decide(self.request, BackendPreference.GPU_FIRST)

        self.assertEqual(BackendKind.CPU, decision.backend)
        self.assertIn("unavailable", decision.reason)

    def test_small_batch_never_pays_gpu_startup_cost(self) -> None:
        dispatcher = BackendDispatcher(
            cpu_backend=FakeBackend(BackendKind.CPU, True),
            cuda_backend=FakeBackend(BackendKind.CUDA, True),
        )
        small_request = GenerationRequest(
            password_count=1,
            password_length=24,
            charset=CharacterSet.NORMAL,
            iterations=1,
            system_mix_enabled=False,
        )

        decision = dispatcher.decide(small_request, BackendPreference.GPU_FIRST)

        self.assertEqual(BackendKind.CPU, decision.backend)
        self.assertIn("below GPU threshold", decision.reason)

    def test_large_batch_uses_cuda_only_after_measured_speedup(self) -> None:
        dispatcher = BackendDispatcher(
            cpu_backend=FakeBackend(BackendKind.CPU, True, delay_seconds=0.004),
            cuda_backend=FakeBackend(BackendKind.CUDA, True, delay_seconds=0.001),
        )

        decision = dispatcher.decide(self.request, BackendPreference.GPU_FIRST)

        self.assertEqual(BackendKind.CUDA, decision.backend)
        self.assertIsNotNone(decision.calibration_cpu_seconds)
        self.assertIsNotNone(decision.calibration_cuda_seconds)

    def test_cpu_only_profile_bypasses_cuda(self) -> None:
        dispatcher = BackendDispatcher(
            cpu_backend=FakeBackend(BackendKind.CPU, True),
            cuda_backend=FakeBackend(BackendKind.CUDA, True),
        )

        decision = dispatcher.decide(self.request, BackendPreference.CPU_ONLY)

        self.assertEqual(BackendKind.CPU, decision.backend)
        self.assertEqual("CPU-only profile selected", decision.reason)


if __name__ == "__main__":
    unittest.main()

"""Messbasierte Backend-Auswahl für PW-Tool."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from time import perf_counter
from typing import Optional

from backends.base import BackendKind, GenerationRequest, GenerationResult
from backends.cpu import CpuBackend
from backends.cuda import CudaBackend


class BackendPreference(str, Enum):
    AUTO = "auto"
    GPU_FIRST = "gpu-first"
    CPU_ONLY = "cpu-only"


@dataclass(frozen=True)
class BackendDecision:
    backend: BackendKind
    reason: str
    calibration_cpu_seconds: Optional[float] = None
    calibration_cuda_seconds: Optional[float] = None


class BackendDispatcher:
    """Wählt CPU oder CUDA anhand realer, secret-freier Laufzeitmessung.

    GPU-first bedeutet: CUDA wird zuerst als Kandidat geprüft. Es bedeutet nicht,
    dass CUDA trotz schlechterer End-to-End-Latenz erzwungen wird. Die Auswahl
    einer GPU verlangt mindestens zehn Prozent gemessenen Zeitgewinn und einen
    ausreichend großen Batch.
    """

    MINIMUM_GPU_BATCH = 128
    REQUIRED_GPU_SPEEDUP = 0.90

    def __init__(self, cpu_backend: Optional[CpuBackend] = None, cuda_backend: Optional[CudaBackend] = None) -> None:
        self.cpu_backend = cpu_backend or CpuBackend()
        self.cuda_backend = cuda_backend or CudaBackend()
        self._calibration: Optional[BackendDecision] = None

    def decide(self, request: GenerationRequest, preference: BackendPreference) -> BackendDecision:
        if preference is BackendPreference.CPU_ONLY:
            return BackendDecision(BackendKind.CPU, "CPU-only profile selected")
        if not self.cuda_backend.is_available():
            return BackendDecision(BackendKind.CPU, "CUDA unavailable; safe CPU fallback")
        if request.password_count < self.MINIMUM_GPU_BATCH:
            return BackendDecision(
                BackendKind.CPU,
                f"Batch below GPU threshold ({request.password_count} < {self.MINIMUM_GPU_BATCH})",
            )

        calibration = self._calibration or self._calibrate(request)
        self._calibration = calibration
        return calibration

    def generate(self, request: GenerationRequest, preference: BackendPreference) -> tuple[GenerationResult, BackendDecision]:
        decision = self.decide(request, preference)
        if decision.backend is BackendKind.CUDA:
            try:
                return self.cuda_backend.generate(request), decision
            except RuntimeError:
                fallback = BackendDecision(
                    BackendKind.CPU,
                    "CUDA generation failed; safe CPU fallback",
                    decision.calibration_cpu_seconds,
                    decision.calibration_cuda_seconds,
                )
                return self.cpu_backend.generate(request), fallback
        return self.cpu_backend.generate(request), decision

    def _calibrate(self, request: GenerationRequest) -> BackendDecision:
        """Vergleicht CPU und CUDA mit einer kleinsten realen, nicht geloggten Probe."""
        calibration_request = GenerationRequest(
            password_count=self.MINIMUM_GPU_BATCH,
            password_length=request.password_length,
            charset=request.charset,
            iterations=request.iterations,
            system_mix_enabled=False,
        )

        cpu_seconds = self._measure_backend(self.cpu_backend, calibration_request)
        cuda_seconds = self._measure_backend(self.cuda_backend, calibration_request)
        if cuda_seconds < cpu_seconds * self.REQUIRED_GPU_SPEEDUP:
            return BackendDecision(
                BackendKind.CUDA,
                "CUDA passed GPU-first calibration for the large-batch workload",
                cpu_seconds,
                cuda_seconds,
            )
        return BackendDecision(
            BackendKind.CPU,
            "CUDA did not meet the required end-to-end speedup; CPU selected",
            cpu_seconds,
            cuda_seconds,
        )

    @staticmethod
    def _measure_backend(backend: CpuBackend | CudaBackend, request: GenerationRequest) -> float:
        start = perf_counter()
        backend.generate(request)
        return perf_counter() - start

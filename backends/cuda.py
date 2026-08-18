"""Optionales CUDA-Backend für große, tatsächlich geeignete Workloads."""

from __future__ import annotations

from time import perf_counter

from backends.base import BackendKind, GenerationRequest, GenerationResult
from cuda_engine import get_cuda_engine
from password_engine import PasswordGenerator
from system_mix import collect_system_mix


class CudaBackend:
    """CUDA-Kandidat mit sicherem Fehler- und Verfügbarkeitsverhalten.

    Dieses Backend führt derzeit keine PBKDF2 auf der GPU aus. Es ist deshalb
    nur ein Kandidat für GPU-Messungen bzw. künftige echte Parallel-Workloads.
    Der Dispatcher darf es erst nach Kalibrierung auswählen.
    """

    kind = BackendKind.CUDA

    def __init__(self) -> None:
        self._engine = get_cuda_engine()

    def is_available(self) -> bool:
        return self._engine.can_generate_secure_passwords()

    @property
    def device_name(self) -> str:
        return self._engine.device_name

    @property
    def unavailable_reason(self) -> str:
        if self._engine.available and not self._engine.can_generate_secure_passwords():
            return "CUDA erkannt, aber kein auditierter sicherer CUDA-Passwortpfad verfügbar"
        return self._engine.error_msg

    def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self.is_available():
            raise RuntimeError("CUDA backend is unavailable")

        timings: dict[str, float] = {}
        start = perf_counter()
        system_mix = collect_system_mix(enabled=request.system_mix_enabled)
        timings["system_mix"] = perf_counter() - start

        entropy, profile = self._engine.gpu_entropy_pbkdf2_profiled(
            iterations=request.iterations,
            hash_length=64,
            system_mix=system_mix,
        )
        timings.update(profile)
        if entropy is None:
            raise RuntimeError("CUDA entropy generation failed")

        start = perf_counter()
        passwords = PasswordGenerator.generate_batch(
            entropy,
            request.password_count,
            request.password_length,
            request.charset,
        )
        timings["password_derivation"] = perf_counter() - start

        return GenerationResult(
            passwords=passwords,
            backend=self.kind,
            system_mix=system_mix,
            phase_seconds=timings,
            worker_count=1,
        )

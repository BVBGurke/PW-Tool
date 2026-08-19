"""CPU-Referenzbackend für sichere Einzel- und Batch-Erzeugung."""

from __future__ import annotations

from time import perf_counter

from backends.base import BackendKind, GenerationRequest, GenerationResult
from cpu_engine import get_cpu_engine
from password_engine import CharacterSet, PasswordGenerator
from system_mix import SystemMixResult, collect_system_mix


class CpuBackend:
    """CPU-Backend ohne unnötige Prozess- oder Thread-Vervielfachung.

    PBKDF2 ist pro Batch der dominante native Aufruf. Für den aktuellen
    Sicherheitsfluss bringt das Aufteilen eines einzelnen KDF-Aufrufs über
    Python-Worker keinen verlässlichen Gewinn und kann Energie verschwenden.
    Batch-Parallellisierung wird deshalb erst nach Benchmarks für unabhängige
    Workloads freigeschaltet.
    """

    kind = BackendKind.CPU

    def __init__(self) -> None:
        self._engine = get_cpu_engine()

    def is_available(self) -> bool:
        return True

    def generate(self, request: GenerationRequest) -> GenerationResult:
        timings: dict[str, float] = {}

        if request.charset is CharacterSet.MAXIMUM:
            start = perf_counter()
            passwords = PasswordGenerator.generate_maximum_batch(
                request.password_count,
                request.password_length,
            )
            timings["os_csprng_password_generation"] = perf_counter() - start
            return GenerationResult(
                passwords=passwords,
                backend=self.kind,
                system_mix=SystemMixResult.disabled(),
                phase_seconds=timings,
                worker_count=1,
            )

        start = perf_counter()
        system_mix = collect_system_mix(enabled=request.system_mix_enabled)
        timings["system_mix"] = perf_counter() - start

        start = perf_counter()
        entropy = self._engine.cpu_entropy_pbkdf2(
            iterations=request.iterations,
            hash_length=64,
            system_mix=system_mix,
        )
        timings["cpu_pbkdf2"] = perf_counter() - start

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

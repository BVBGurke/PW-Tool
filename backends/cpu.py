"""CPU-Referenzbackend für sichere Einzel- und Batch-Erzeugung."""

from __future__ import annotations

from time import perf_counter

from backends.base import BackendKind, GenerationRequest, GenerationResult
from password_engine import PasswordGenerator
from system_mix import SystemMixResult


class CpuBackend:
    """CPU-Backend ohne unnötige Prozess- oder Thread-Vervielfachung.

    PBKDF2 ist pro Batch der dominante native Aufruf. Für den aktuellen
    Sicherheitsfluss bringt das Aufteilen eines einzelnen KDF-Aufrufs über
    Python-Worker keinen verlässlichen Gewinn und kann Energie verschwenden.
    Batch-Parallellisierung wird deshalb erst nach Benchmarks für unabhängige
    Workloads freigeschaltet.
    """

    kind = BackendKind.CPU

    def is_available(self) -> bool:
        return True

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Erzeugt alle sichtbaren Passwortprofile direkt aus dem OS-CSPRNG."""
        start = perf_counter()
        passwords = PasswordGenerator.generate_policy_batch(
            request.password_count,
            request.password_length,
            request.charset,
        )
        timings = {"os_csprng_password_generation": perf_counter() - start}
        return GenerationResult(
            passwords=passwords,
            backend=self.kind,
            system_mix=SystemMixResult.disabled(),
            phase_seconds=timings,
            worker_count=1,
        )

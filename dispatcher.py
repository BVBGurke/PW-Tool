"""Eindeutige Backend-Auswahl für lokale CSPRNG-Passworterzeugung."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from backends.base import BackendKind, GenerationRequest, GenerationResult
from backends.cpu import CpuBackend
from backends.cuda import CudaBackend


class BackendPreference(str, Enum):
    """Historische Präferenzwerte für kompatible Aufrufer.

    Die sichtbaren Passwortprofile ignorieren diese Präferenz bewusst, weil sie
    immer den direkten, auditierbaren OS-CSPRNG-CPU-Pfad verwenden.
    """

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
    """Leitet alle sichtbaren Passwortprofile eindeutig an das CPU-Backend weiter."""

    def __init__(
        self,
        cpu_backend: Optional[CpuBackend] = None,
        cuda_backend: Optional[CudaBackend] = None,
    ) -> None:
        self.cpu_backend = cpu_backend or CpuBackend()
        # Nur Kompatibilität mit bestehenden Aufrufern; der sichtbare Pfad nutzt es nicht.
        self.cuda_backend = cuda_backend

    def decide(self, request: GenerationRequest, preference: BackendPreference) -> BackendDecision:
        """Wählt den einzigen sichtbaren, direkten OS-CSPRNG-Pfad."""
        del request, preference
        return BackendDecision(
            BackendKind.CPU,
            "Visible password profiles use direct OS-CSPRNG on the CPU",
        )

    def generate(
        self,
        request: GenerationRequest,
        preference: BackendPreference,
    ) -> tuple[GenerationResult, BackendDecision]:
        """Erzeugt einen Batch nur über den lokalen CSPRNG-CPU-Pfad."""
        decision = self.decide(request, preference)
        return self.cpu_backend.generate(request), decision

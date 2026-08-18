"""CLI für reproduzierbare PW-Tool-Backend-Benchmarks.

Das Skript gibt ausschließlich Profil- und Metrikdaten aus, niemals erzeugte
Passwörter, Seeds, Systemmix-Digests oder Quellpfade.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backends.base import BackendKind, GenerationRequest
from backends.cpu import CpuBackend
from backends.cuda import CudaBackend
from benchmark.profiles import WorkloadClass, resolve_profile
from benchmark.runner import BenchmarkRunner, PhaseRecorder
from dispatcher import BackendDispatcher, BackendPreference
from password_engine import CharacterSet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PW-Tool performance benchmark")
    parser.add_argument("--profile", choices=[item.value for item in WorkloadClass], default="small")
    parser.add_argument("--backend", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--memory", action="store_true", help="Track Python allocation peak")
    parser.add_argument("--json", action="store_true", help="Emit a single JSON result")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = resolve_profile(args.profile)
    request = GenerationRequest(
        password_count=profile.password_count,
        password_length=profile.password_length,
        charset=CharacterSet.COMPLETE,
        iterations=profile.iterations,
        system_mix_enabled=False,
    )

    dispatcher = BackendDispatcher()
    preference = {
        "auto": BackendPreference.AUTO,
        "cpu": BackendPreference.CPU_ONLY,
        "cuda": BackendPreference.GPU_FIRST,
    }[args.backend]
    decision = dispatcher.decide(request, preference)
    if args.backend == "cuda" and decision.backend is not BackendKind.CUDA:
        print(f"CUDA benchmark unavailable: {decision.reason}", file=sys.stderr)
        return 2

    backend = dispatcher.cuda_backend if decision.backend is BackendKind.CUDA else dispatcher.cpu_backend

    def operation(recorder: PhaseRecorder) -> None:
        result = backend.generate(request)
        for phase_name, seconds in result.phase_seconds.items():
            # Das Backend liefert nur Zeitwerte, niemals Secret-Material.
            recorder.add_duration(phase_name, seconds)

    result = BenchmarkRunner().run(
        backend=decision.backend.value,
        workload=profile.name.value,
        units_per_run=profile.password_count,
        operation=operation,
        warmups=args.warmups,
        repeats=args.repeats,
        capture_python_memory=args.memory,
    )
    output = {
        **result.to_dict(),
        "decision": {
            "backend": decision.backend.value,
            "reason": decision.reason,
            "calibration_cpu_seconds": decision.calibration_cpu_seconds,
            "calibration_cuda_seconds": decision.calibration_cuda_seconds,
        },
    }

    if args.json:
        print(json.dumps(output, sort_keys=True))
    else:
        summary = result.summary
        print(f"Profile: {profile.name.value}; backend: {decision.backend.value}")
        print(f"Decision: {decision.reason}")
        print(f"Median: {summary.median_seconds:.6f}s; p95: {summary.p95_seconds:.6f}s")
        print(f"Throughput: {summary.throughput_per_second:.2f} passwords/s")
        if summary.peak_python_bytes is not None:
            print(f"Python allocation peak: {summary.peak_python_bytes} bytes")
        for name, seconds in sorted(result.phase_median_seconds.items()):
            print(f"Phase {name}: {seconds:.6f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

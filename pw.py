"""Interaktiver Einstiegspunkt für die reine Python-CLI von PW-Tool."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from backends.base import GenerationRequest
from cuda_engine import get_cuda_engine
from diagnostics import SafeDiagnosticLogger
from dispatcher import BackendDispatcher, BackendPreference
from password_engine import CharacterSet
from profiles import ProfileOption, SessionProfiles
from textual_ui import PwToolTextualApp
from version import __version__


class PasswordGeneratorApp:
    """Orchestriert sichere Erzeugung, Backend-Auswahl und TUI ohne Secret-Logging."""

    def __init__(self, *, log_enabled: bool = False, log_directory: Path | None = None) -> None:
        self.cuda_engine = get_cuda_engine()
        self.dispatcher = BackendDispatcher()
        self.logger = SafeDiagnosticLogger(enabled=log_enabled, directory=log_directory)

    def generate_with_mode(
        self,
        password_count: int,
        password_length: int,
        charset: CharacterSet,
        overkill: bool,
        system_mix_enabled: bool,
        profiles: SessionProfiles,
    ) -> tuple:
        """Erzeugt einen Batch über den messbasiert ausgewählten sicheren Backendpfad."""
        iterations = 1_000_000 if overkill else 200_000
        request = GenerationRequest(
            password_count=password_count,
            password_length=password_length,
            charset=charset,
            iterations=iterations,
            system_mix_enabled=system_mix_enabled,
        )
        preference = (
            BackendPreference.GPU_FIRST
            if profiles.is_enabled(ProfileOption.GPU_FIRST)
            else BackendPreference.CPU_ONLY
        )
        result, decision = self.dispatcher.generate(request, preference)

        self.logger.log(
            "backend_selected",
            backend_selected=result.backend.value,
            fallback_reason=decision.reason,
            batch_count=password_count,
            password_length=password_length,
            iterations=iterations,
            profile_flags=profiles.labels(),
            cuda_available=self.cuda_engine.available,
        )
        for phase, seconds in result.phase_seconds.items():
            self.logger.log(
                "phase_timing",
                backend=result.backend.value,
                phase=phase,
                duration_ms=round(seconds * 1000, 3),
            )

        return result, decision

    def run_interactive(self) -> None:
        """Startet die responsive Textual-Oberfläche mit der sicheren Kernlogik."""
        cuda_available, device_name, _ = self.cuda_engine.get_status()
        application = PwToolTextualApp(
            self.generate_with_mode,
            cuda_available=cuda_available,
            device_name=device_name,
            log_enabled=self.logger.enabled,
        )
        application.run()

    def run(self) -> int:
        try:
            self.run_interactive()
            return 0
        except Exception as error:
            print(f"Fatal error: {error}", file=sys.stderr)
            return 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PW-Tool – lokale Python-Passwort-CLI")
    parser.add_argument("--version", action="version", version=f"PW-Tool {__version__}")
    parser.add_argument(
        "-log",
        "--log",
        action="store_true",
        dest="log_enabled",
        help="Aktiviert redigierte lokale Diagnose-JSONL-Dateien; niemals Passwörter oder Seeds.",
    )
    parser.add_argument(
        "--log-directory",
        type=Path,
        default=None,
        help="Optionales lokales Zielverzeichnis für -log-Dateien.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    app = PasswordGeneratorApp(log_enabled=args.log_enabled, log_directory=args.log_directory)
    raise SystemExit(app.run())


if __name__ == "__main__":
    main()

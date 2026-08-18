"""
Rich-Based Terminal User Interface for Password Generator.

Provides interactive menus for password generation with real-time progress tracking.
Supports non-blocking GPU computation using threading.
"""

import time
import threading
from dataclasses import dataclass
from typing import Optional, Callable, Any
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from password_engine import CharacterSet, PasswordGenerator, parse_charset_input
from system_mix import SystemMixStatus
from profiles import ProfileOption, SessionProfiles


@dataclass(frozen=True)
class GenerationUiConfig:
    """Einmalig erfasste Einstellungen für alle Wiederholungen der Sitzung."""

    password_length: int
    charset: CharacterSet
    system_mix_enabled: bool
    overkill: bool
    password_count: int


class RichUI:
    """Terminal UI for password generation with Rich library."""

    def __init__(self, cuda_available: bool, device_name: str = "", console: Optional[Console] = None):
        """
        Initialize Rich UI.
        
        Args:
            cuda_available: Whether CUDA/GPU is available
            device_name: Name of CUDA device (empty if not available)
        """
        if not RICH_AVAILABLE:
            raise RuntimeError(
                "Rich library not installed. Install with: pip install rich"
            )
        
        self.console = console or Console()
        self.cuda_available = cuda_available
        self.device_name = device_name
        self.computation_thread = None
        self.computation_result = None
        self.computation_error = None
        self.computation_time = 0.0

    @property
    def is_compact(self) -> bool:
        """Erkennt schmale Terminalfenster, etwa mobile Termux-Sitzungen."""
        return self.console.size.width < 72

    def show_header(self) -> None:
        """Display application header with system status."""
        header_text = "LOKALER PYTHON-PASSWORTGENERATOR"
        
        status = "CUDA erkannt" if self.cuda_available else "CPU-Modus (kein CUDA)"
        device_info = f"Gerät: {self.device_name}" if self.device_name else "Nur CPU"
        
        self.console.print()
        if self.is_compact:
            self.console.print(f"[bold cyan]{header_text}[/bold cyan]")
            self.console.print(f"{status} · {device_info}")
        else:
            self.console.print(
                Panel(
                    f"{header_text}\n{status}\n{device_info}",
                    style="bold cyan",
                    expand=False,
                )
            )
        self.console.print()

    def get_session_profiles(self) -> SessionProfiles:
        """Erfasst die wirksamen Beta-Optionen genau einmal pro Sitzung."""
        self.console.print("[bold]Beta-Optionen (einmalig):[/bold]")
        self.console.print("  1 – CUDA als Kandidat prüfen; sicherer CPU-Fallback bleibt aktiv")
        self.console.print("  2 – zusätzliche, nicht sensitive Phasenzeiten anzeigen")
        choice = Prompt.ask(
            "Aktive Optionen (z. B. 1 2; Enter = 1)",
            default="",
            console=self.console,
        ).strip()
        try:
            return SessionProfiles.from_selection(choice)
        except ValueError as error:
            self.console.print(f"[yellow]{error} Standardoption 1 wird verwendet.[/yellow]")
            return SessionProfiles()

    def get_generation_config(self) -> GenerationUiConfig:
        """Fragt alle Generierungseinstellungen einmalig ab und fixiert sie für die Sitzung."""
        self.console.print("[bold]Generierungseinstellungen (einmalig):[/bold]")
        return GenerationUiConfig(
            password_length=self.get_password_length(),
            charset=self.get_character_set(),
            system_mix_enabled=self.get_system_mix_enabled(),
            overkill=self.get_overkill_mode(),
            password_count=self.get_batch_count(),
        )

    def show_backend_decision(self, backend: str, reason: str, logging_enabled: bool) -> None:
        """Zeigt die sichere Backendentscheidung ohne Messgeheimnisse."""
        logging = "Diagnoselog aktiv" if logging_enabled else "Kein Diagnoselog"
        if self.is_compact:
            self.console.print(f"[bold]Backend:[/bold] {backend.upper()}")
            self.console.print(f"[dim]{reason}[/dim]")
            self.console.print(f"[dim]{logging}[/dim]")
        else:
            self.console.print(
                Panel(
                    f"Backend: {backend.upper()}\n{reason}\n{logging}",
                    title="Ausführungsentscheidung",
                    style="bold green" if backend == "cuda" else "bold cyan",
                    expand=False,
                )
            )

    def get_password_length(self) -> int:
        """
        Prompt user for password length.
        
        Returns:
            Password length (8-256).
        """
        while True:
            try:
                length_str = Prompt.ask(
                    "[yellow]Passwortlänge[/yellow]",
                    default="64",
                    console=self.console
                )
                length = int(length_str)
                if PasswordGenerator.validate_length(length):
                    return length
                else:
                    self.console.print(
                        "[red]✗ Die Länge muss zwischen 8 und 256 liegen.[/red]"
                    )
            except ValueError:
                self.console.print("[red]✗ Bitte eine gültige Zahl eingeben.[/red]")

    def get_character_set(self) -> CharacterSet:
        """
        Prompt user for character set selection.
        
        Returns:
            CharacterSet enum value.
        """
        self.console.print()
        self.console.print("[bold]Zeichensatz:[/bold]")
        self.console.print("  [cyan]1[/cyan] - Standard (Buchstaben + Ziffern)")
        self.console.print("  [cyan]2[/cyan] - Vollständig (+ Sonderzeichen)")
        
        while True:
            try:
                choice = Prompt.ask(
                    "Select",
                    default="1",
                    console=self.console
                )
                return parse_charset_input(choice)
            except ValueError:
                self.console.print("[red]✗ Bitte 1 oder 2 eingeben.[/red]")

    def get_system_mix_enabled(self) -> bool:
        """Fragt ab, ob die lokale, feste Systemdatei-Allowlist genutzt werden soll."""
        self.console.print()
        return Confirm.ask(
            "[bold]Automatische lokale Systemdatei-Mischung aktivieren?[/bold] "
            "(nur feste, nicht sensible Dateien; Standard: Ja)",
            default=True,
            console=self.console,
        )

    def get_overkill_mode(self) -> bool:
        """
        Prompt user for Overkill Mode.
        
        Returns:
            True if Overkill Mode enabled, False otherwise.
        """
        self.console.print()
        overkill = Confirm.ask(
            "[bold]Zusätzliche KDF-Arbeit aktivieren?[/bold] "
            "(langsamer; keine zusätzliche Zufallsentropie)",
            default=False,
            console=self.console
        )
        return overkill

    def get_batch_count(self) -> int:
        """
        Prompt user for batch count.
        
        Returns:
            Number of passwords to generate (1+).
        """
        while True:
            try:
                count_str = Prompt.ask(
                    "[yellow]Anzahl der Passwörter[/yellow]",
                    default="1",
                    console=self.console
                )
                count = int(count_str)
                from backends.base import MAX_BATCH_COUNT
                if 1 <= count <= MAX_BATCH_COUNT:
                    return count
                self.console.print(
                    f"[red]✗ Anzahl muss zwischen 1 und {MAX_BATCH_COUNT} liegen.[/red]"
                )
            except ValueError:
                self.console.print("[red]✗ Bitte eine gültige Zahl eingeben.[/red]")

    def run_computation_threaded(
        self,
        compute_func: Callable[[], Any],
        description: str = "Computing..."
    ) -> Any:
        """
        Run a long-running computation in a background thread with progress bar.
        
        Args:
            compute_func: Callable that returns computation result
            description: Progress bar description
            
        Returns:
            Result from compute_func.
        """
        self.computation_result = None
        self.computation_error = None
        start_time = time.time()
        
        def thread_target():
            try:
                self.computation_result = compute_func()
            except Exception as e:
                self.computation_error = e
            finally:
                self.computation_time = time.time() - start_time

        thread = threading.Thread(target=thread_target, daemon=True)
        thread.start()

        # Show progress spinner while computing
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(description, total=None)
            
            while thread.is_alive():
                thread.join(timeout=0.1)

        if self.computation_error:
            raise self.computation_error

        return self.computation_result

    def display_passwords(
        self,
        passwords: list,
        execution_mode: str = "GPU",
        system_mix_status: SystemMixStatus = SystemMixStatus.DISABLED,
        system_mix_sources: int = 0,
    ) -> None:
        """
        Display generated passwords in a formatted table.
        
        Args:
            passwords: List of password strings
            execution_mode: "GPU" or "CPU" (for display)
        """
        self.console.print()
        if self.is_compact:
            self.console.print("[bold]Generierte Passwörter:[/bold]")
            for idx, pwd in enumerate(passwords, 1):
                # Falten statt Ellipse: Jedes Passwortzeichen bleibt sichtbar.
                self.console.print(f"{idx}: {pwd}", style="bold green", overflow="fold")
        else:
            table = Table(title="Generierte Passwörter", show_header=True)
            table.add_column("#", style="cyan", width=5)
            table.add_column("Passwort", style="bold green", overflow="fold")
            for idx, pwd in enumerate(passwords, 1):
                table.add_row(str(idx), pwd)
            self.console.print(table)

        # Summary
        self.console.print()
        summary = f"[cyan]{len(passwords)} Passwort/Passwörter in {self.computation_time:.2f}s erzeugt ({execution_mode})[/cyan]"
        self.console.print(summary)
        self.console.print(self._system_mix_summary(system_mix_status, system_mix_sources))

    def _system_mix_summary(
        self,
        status: SystemMixStatus,
        source_count: int,
    ) -> str:
        if status is SystemMixStatus.COMPLETE:
            return f"[green]Systemmix aktiv: {source_count} lokale, feste Quellen wurden gehasht.[/green]"
        if status is SystemMixStatus.PARTIAL:
            return "[yellow]Systemmix unvollständig: Sicherer Systemzufall wurde ohne Dateimix verwendet.[/yellow]"
        if status is SystemMixStatus.UNAVAILABLE:
            return "[yellow]Systemmix nicht verfügbar: Sicherer Systemzufall wurde ohne Dateimix verwendet.[/yellow]"
        return "[cyan]Systemmix deaktiviert: Sicherer Systemzufall wurde verwendet.[/cyan]"

    def show_error(self, title: str, message: str) -> None:
        """
        Display an error message.
        
        Args:
            title: Error title
            message: Error details
        """
        self.console.print()
        if self.is_compact:
            self.console.print(f"[bold red]{title}:[/bold red] {message}", overflow="fold")
        else:
            self.console.print(
                Panel(
                    message,
                    title=title,
                    style="bold red",
                    expand=False,
                )
            )
        self.console.print()

    def show_fallback_notice(self) -> None:
        """Display notice that system fell back to CPU mode."""
        self.console.print(
            Panel(
                "CUDA-Beschleunigung ist nicht verfügbar. CPU-Modus wird verwendet.",
                title="Fallback auf CPU",
                style="bold yellow",
                expand=False
            )
        )
        self.console.print()

    def prompt_continue(self) -> bool:
        """
        Prompt user to continue or exit.
        
        Returns:
            True to continue, False to exit.
        """
        self.console.print()
        return Confirm.ask(
            "[bold]Mit derselben Konfiguration erneut erzeugen?[/bold]",
            default=False,
            console=self.console
        )

    def show_goodbye(self) -> None:
        """Display exit message."""
        self.console.print()
        if self.is_compact:
            self.console.print("[bold cyan]Vielen Dank für die Nutzung von PW-Tool.[/bold cyan]")
        else:
            self.console.print(
                Panel(
                    "Vielen Dank für die Nutzung von PW-Tool.",
                    style="bold cyan",
                    expand=False,
                )
            )
        self.console.print()

"""Responsive Textual-Oberfläche für die lokale PW-Tool-Beta.

Die App speichert ausschließlich nicht sensible Sitzungseinstellungen. Passwortwerte
werden nur im sichtbaren Ergebnisbereich ausgegeben und niemals an den
Diagnoselogger übergeben.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.events import Resize
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Select, Static

from backends.base import GenerationResult, MAX_BATCH_COUNT
from dispatcher import BackendDecision
from password_engine import CharacterSet, PasswordGenerator
from profiles import ProfileOption, SessionProfiles


GenerationCallback = Callable[
    [int, int, CharacterSet, bool, bool, SessionProfiles],
    tuple[GenerationResult, BackendDecision],
]


@dataclass(frozen=True)
class GenerationForm:
    """Nicht sensible, einmalig im Formular bearbeitbare Sitzungswerte."""

    password_length: int
    password_count: int
    charset: CharacterSet
    system_mix_enabled: bool
    extra_kdf_work: bool
    profiles: SessionProfiles


class PwToolTextualApp(App[None]):
    """Mobile-freundliche Textual-TUI mit sicherer Hintergrundberechnung."""

    TITLE = "PW-Tool"
    SUB_TITLE = "Lokaler Passwortgenerator"
    COMPACT_WIDTH = 72

    CSS = """
    Screen {
        background: #10151c;
    }

    #main {
        width: 96%;
        max-width: 112;
        height: auto;
        margin: 1 2;
    }

    #runtime-status, #status, #backend, #metrics {
        height: auto;
        margin: 0 0 1 0;
    }

    #configuration {
        grid-size: 2;
        grid-gutter: 1 2;
        height: auto;
        margin: 1 0;
    }

    .field {
        height: auto;
    }

    .field Label {
        margin: 0 0 1 0;
    }

    #actions {
        height: auto;
        align-horizontal: center;
        margin: 1 0;
    }

    #generate, #copy {
        min-width: 22;
        margin: 0 1;
    }

    #results {
        height: auto;
        min-height: 7;
        max-height: 1fr;
        overflow-y: auto;
        overflow-x: auto;
        border: round #5e9cff;
        padding: 1;
        text-wrap: wrap;
    }

    .compact #main {
        width: 100%;
        margin: 0;
    }

    .compact #configuration {
        grid-size: 1;
        grid-gutter: 1;
    }

    .compact #actions {
        layout: vertical;
        align-horizontal: center;
    }

    .compact #generate, .compact #copy {
        width: 1fr;
        margin: 0 0 1 0;
    }

    .invalid {
        border: heavy #e05252;
    }
    """

    BINDINGS = [
        Binding("ctrl+g", "generate", "Erzeugen", show=True),
        Binding("ctrl+c", "copy_passwords", "Kopieren", show=True),
        Binding("ctrl+q", "quit", "Beenden", show=True),
    ]

    def __init__(
        self,
        generate_callback: GenerationCallback,
        *,
        cuda_available: bool,
        device_name: str,
        log_enabled: bool,
    ) -> None:
        super().__init__()
        self._generate_callback = generate_callback
        self._cuda_available = cuda_available
        self._device_name = device_name
        self._log_enabled = log_enabled
        self._last_passwords: tuple[str, ...] = ()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="main"):
            cuda_status = (
                f"CUDA erkannt: {self._device_name or 'unbekanntes Gerät'}"
                if self._cuda_available
                else "CPU-Modus: CUDA nicht verfügbar"
            )
            log_status = "Diagnoselog aktiv (-log)" if self._log_enabled else "Kein Diagnoselog"
            yield Static(f"[bold]Lokale Ausführung[/bold] · {cuda_status} · {log_status}", id="runtime-status")
            yield Static("[bold]Konfiguration[/bold] – Werte einmal einstellen und mit „Erzeugen“ erneut verwenden.")
            with Grid(id="configuration"):
                with Vertical(classes="field"):
                    yield Label("Passwortlänge (8–256)")
                    yield Input("64", id="password-length", type="integer")
                with Vertical(classes="field"):
                    yield Label(f"Anzahl der Passwörter (1–{MAX_BATCH_COUNT})")
                    yield Input("1", id="password-count", type="integer")
                with Vertical(classes="field"):
                    yield Label("Zeichensatz")
                    yield Select(
                        [
                            ("Standard: Buchstaben + Ziffern", CharacterSet.NORMAL.value),
                            ("Vollständig: zusätzlich Sonderzeichen", CharacterSet.COMPLETE.value),
                        ],
                        value=CharacterSet.NORMAL.value,
                        allow_blank=False,
                        id="charset",
                    )
                with Vertical(classes="field"):
                    yield Label("Backend und Anzeige")
                    yield Checkbox("CUDA als Kandidat prüfen", value=True, id="gpu-first")
                    yield Checkbox("Nicht sensitive Phasenzeiten anzeigen", value=False, id="show-metrics")
                with Vertical(classes="field"):
                    yield Label("Lokaler Zusatzmix")
                    yield Checkbox(
                        "Feste, nicht sensible Systemdateien hashen",
                        value=True,
                        id="system-mix",
                    )
                with Vertical(classes="field"):
                    yield Label("Rechenaufwand")
                    yield Checkbox(
                        "Zusätzliche KDF-Arbeit (keine zusätzliche Zufallsentropie)",
                        value=False,
                        id="extra-kdf",
                    )
            with Horizontal(id="actions"):
                yield Button("Passwörter erzeugen", id="generate", variant="primary")
                yield Button("Ergebnis kopieren", id="copy", disabled=True)
            yield Static("Bereit. Die Erzeugung läuft lokal.", id="status")
            yield Static("Noch keine Passwörter erzeugt.", id="backend")
            yield Static("", id="metrics")
            yield Static("Noch keine Ergebnisse.", id="results", markup=False)
        yield Footer()

    def on_mount(self) -> None:
        self._apply_layout_scale(self.size.width)
        self.query_one("#password-length", Input).focus()

    def on_resize(self, event: Resize) -> None:
        self._apply_layout_scale(event.size.width)

    def _apply_layout_scale(self, width: int) -> None:
        self.screen.set_class(width < self.COMPACT_WIDTH, "compact")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate":
            self.action_generate()
        elif event.button.id == "copy":
            self.action_copy_passwords()

    def action_generate(self) -> None:
        form = self._read_form()
        if form is None:
            return
        self.query_one("#generate", Button).disabled = True
        self.query_one("#status", Static).update("[yellow]Berechne lokal …[/yellow]")
        self._generate_in_worker(form)

    def action_copy_passwords(self) -> None:
        if not self._last_passwords:
            self.query_one("#status", Static).update("[yellow]Es gibt noch kein Ergebnis zum Kopieren.[/yellow]")
            return
        try:
            self.copy_to_clipboard("\n".join(self._last_passwords))
        except Exception:
            self.query_one("#status", Static).update(
                "[yellow]Zwischenablage ist in dieser Terminalumgebung nicht verfügbar.[/yellow]"
            )
        else:
            self.query_one("#status", Static).update("[green]Ergebnis in die Zwischenablage kopiert.[/green]")

    def _read_form(self) -> GenerationForm | None:
        length_input = self.query_one("#password-length", Input)
        count_input = self.query_one("#password-count", Input)
        charset_select = self.query_one("#charset", Select)
        length_input.remove_class("invalid")
        count_input.remove_class("invalid")

        try:
            password_length = int(length_input.value)
        except ValueError:
            password_length = 0
        try:
            password_count = int(count_input.value)
        except ValueError:
            password_count = 0

        invalid = False
        if not PasswordGenerator.validate_length(password_length):
            length_input.add_class("invalid")
            invalid = True
        if not 1 <= password_count <= MAX_BATCH_COUNT:
            count_input.add_class("invalid")
            invalid = True
        if invalid:
            self.query_one("#status", Static).update(
                f"[red]Länge muss 8–256 und Anzahl 1–{MAX_BATCH_COUNT} sein.[/red]"
            )
            return None

        charset_value = str(charset_select.value)
        charset = CharacterSet(charset_value)
        enabled: set[ProfileOption] = set()
        if self.query_one("#gpu-first", Checkbox).value:
            enabled.add(ProfileOption.GPU_FIRST)
        if self.query_one("#show-metrics", Checkbox).value:
            enabled.add(ProfileOption.BENCHMARK_METRICS)

        return GenerationForm(
            password_length=password_length,
            password_count=password_count,
            charset=charset,
            system_mix_enabled=self.query_one("#system-mix", Checkbox).value,
            extra_kdf_work=self.query_one("#extra-kdf", Checkbox).value,
            profiles=SessionProfiles(enabled=enabled),
        )

    @work(thread=True, exclusive=True)
    def _generate_in_worker(self, form: GenerationForm) -> None:
        """Führt die KDF außerhalb des UI-Threads aus und aktualisiert die UI sicher."""
        try:
            result, decision = self._generate_callback(
                form.password_count,
                form.password_length,
                form.charset,
                form.extra_kdf_work,
                form.system_mix_enabled,
                form.profiles,
            )
        except Exception:
            self.call_from_thread(self._show_generation_error)
            return
        self.call_from_thread(self._show_generation_result, result, decision)

    def _show_generation_error(self) -> None:
        self.query_one("#generate", Button).disabled = False
        self.query_one("#status", Static).update(
            "[red]Die Erzeugung ist fehlgeschlagen. Bitte Eingaben und Backendstatus prüfen.[/red]"
        )

    def _show_generation_result(self, result: GenerationResult, decision: BackendDecision) -> None:
        self.query_one("#generate", Button).disabled = False
        self._last_passwords = tuple(result.passwords)
        self.query_one("#copy", Button).disabled = not bool(self._last_passwords)
        self.query_one("#status", Static).update(
            f"[green]{len(result.passwords)} Passwort/Passwörter lokal erzeugt.[/green]"
        )
        self.query_one("#backend", Static).update(
            "[bold]Backend:[/bold] "
            f"{result.backend.value.upper()}\n{decision.reason}\n"
            f"Systemmix: {result.system_mix.status.value} ({result.system_mix.source_count} Quellen)"
        )
        self.query_one("#results", Static).update(
            "Generierte Passwörter\n"
            + "\n".join(f"{index}: {value}" for index, value in enumerate(result.passwords, 1))
        )
        metrics = self.query_one("#show-metrics", Checkbox).value
        metrics_output = self.query_one("#metrics", Static)
        if metrics:
            phases = "\n".join(
                f"{phase}: {seconds * 1000:.3f} ms"
                for phase, seconds in sorted(result.phase_seconds.items())
            )
            metrics_output.update(f"[bold]Messphasen[/bold]\n{phases}")
        else:
            metrics_output.update("")

"""Textual-TUI für lokale, direkte OS-CSPRNG-Passworterzeugung.

Die Oberfläche hält nur nicht sensible Sitzungseinstellungen. Passwortwerte,
Salts, Hashwerte und abgeleitete Bytes werden weder protokolliert noch in der
Hash-Demo ausgegeben.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Vertical
from textual.events import Resize
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from backends.base import GenerationResult, MAX_BATCH_COUNT
from dispatcher import BackendDecision
from hash_demo import LocalHashDemoReport, run_local_hash_demo
from password_engine import (
    CharacterSet,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    PasswordGenerator,
)
from profiles import SessionProfiles
from security_check import assess_generated_passwords


GenerationCallback = Callable[
    [int, int, CharacterSet, bool, bool, SessionProfiles],
    tuple[GenerationResult, BackendDecision],
]


@dataclass(frozen=True)
class GenerationForm:
    """Die drei sichtbaren, nicht sensiblen Sitzungseinstellungen."""

    password_length: int
    password_count: int
    charset: CharacterSet


class PwToolTextualApp(App[None]):
    """Mobile-freundliche Textual-TUI mit direkter OS-CSPRNG-Erzeugung."""

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

    #runtime-status, #status, #backend, #security-check, #hash-demo {
        height: auto;
        margin: 0 0 1 0;
    }

    #configuration {
        grid-size: 3;
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
        grid-size: 5;
        grid-gutter: 1;
        height: auto;
        margin: 1 0;
    }

    #generate, #copy, #check, #hash-demo-button, #clear {
        min-width: 14;
    }

    #security-check, #hash-demo, #results {
        border: round #5e9cff;
        padding: 1;
    }

    #results {
        min-height: 7;
        max-height: 1fr;
        overflow-y: auto;
        overflow-x: auto;
        text-wrap: wrap;
    }

    .compact #main {
        width: 100%;
        height: 1fr;
        margin: 0;
        padding: 0 1;
        overflow-y: auto;
    }

    .compact #runtime-status {
        margin-top: 1;
    }

    .compact #configuration, .compact #actions {
        grid-size: 1;
        grid-gutter: 1;
    }

    .compact #generate, .compact #copy, .compact #check,
    .compact #hash-demo-button, .compact #clear {
        width: 1fr;
        min-height: 3;
    }

    .invalid {
        border: heavy #e05252;
    }
    """

    BINDINGS = [
        Binding("ctrl+g", "generate", "Erzeugen", show=True),
        Binding("ctrl+c", "copy_passwords", "Kopieren", show=True),
        Binding("ctrl+s", "check_passwords", "Prüfen", show=True),
        Binding("ctrl+h", "run_hash_demo", "Hash-Demo", show=True),
        Binding("ctrl+l", "clear_passwords", "Löschen", show=True),
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
        # Argumente bleiben mit dem CLI-Einstieg kompatibel, sind aber keine UI-Optionen.
        self._cuda_available = cuda_available
        self._device_name = device_name
        self._log_enabled = log_enabled
        self._last_passwords: tuple[str, ...] = ()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="main"):
            log_status = "Diagnoselog aktiv" if self._log_enabled else "Kein Diagnoselog"
            yield Static(
                f"Lokale Ausführung · direkter OS-CSPRNG-CPU-Pfad · {log_status}",
                id="runtime-status",
                markup=False,
            )
            yield Static(
                "Konfiguration einmal wählen; jede Erzeugung verwendet dieselben Werte.",
                markup=False,
            )
            with Grid(id="configuration"):
                with Vertical(classes="field"):
                    yield Label(f"Passwortlänge ({MIN_PASSWORD_LENGTH}–{MAX_PASSWORD_LENGTH})")
                    yield Input("64", id="password-length", type="integer")
                with Vertical(classes="field"):
                    yield Label(f"Anzahl der Passwörter (1–{MAX_BATCH_COUNT})")
                    yield Input("1", id="password-count", type="integer")
                with Vertical(classes="field"):
                    yield Label("Zeichenauswahl")
                    yield Select(
                        [
                            ("Vollständig: alle Klassen, Sonderzeichen garantiert", CharacterSet.COMPLETE.value),
                            ("Kompatibel: Buchstaben + Ziffern", CharacterSet.NORMAL.value),
                        ],
                        value=CharacterSet.COMPLETE.value,
                        allow_blank=False,
                        id="charset",
                    )
            with Grid(id="actions"):
                yield Button("Erzeugen", id="generate", variant="primary")
                yield Button("Kopieren", id="copy", disabled=True)
                yield Button("Sicherheitscheck", id="check", disabled=True)
                yield Button("Hash-Demo", id="hash-demo-button")
                yield Button("Ergebnisse löschen", id="clear", disabled=True)
            yield Static("Bereit. Die Erzeugung läuft ausschließlich lokal.", id="status")
            yield Static("Noch keine Passwörter erzeugt.", id="backend", markup=False)
            yield Static("Noch kein Sicherheitscheck durchgeführt.", id="security-check", markup=False)
            yield Static("Noch keine Hash-Demo ausgeführt.", id="hash-demo", markup=False)
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
        elif event.button.id == "check":
            self.action_check_passwords()
        elif event.button.id == "hash-demo-button":
            self.action_run_hash_demo()
        elif event.button.id == "clear":
            self.action_clear_passwords()

    def action_generate(self) -> None:
        form = self._read_form()
        if form is None:
            return
        self.query_one("#generate", Button).disabled = True
        self.query_one("#status", Static).update("[yellow]Erzeuge lokal …[/yellow]")
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

    def action_check_passwords(self) -> None:
        if not self._last_passwords:
            self.query_one("#status", Static).update(
                "[yellow]Für den Sicherheitscheck zuerst Passwörter erzeugen.[/yellow]"
            )
            return
        charset = CharacterSet(str(self.query_one("#charset", Select).value))
        report = assess_generated_passwords(self._last_passwords, charset)
        self.query_one("#security-check", Static).update(report.as_text())
        self.query_one("#status", Static).update(
            "[green]Sicherheitscheck lokal abgeschlossen; keine Passwortwerte gespeichert.[/green]"
        )

    def action_run_hash_demo(self) -> None:
        form = self._read_form()
        if form is None:
            return
        self.query_one("#hash-demo-button", Button).disabled = True
        self.query_one("#status", Static).update("[yellow]Führe lokale Hash-Demo aus …[/yellow]")
        self._hash_demo_in_worker(form)

    def action_clear_passwords(self) -> None:
        self._last_passwords = ()
        self.query_one("#copy", Button).disabled = True
        self.query_one("#check", Button).disabled = True
        self.query_one("#clear", Button).disabled = True
        self.query_one("#results", Static).update("Ergebnisse aus der Oberfläche entfernt.")
        self.query_one("#security-check", Static).update(
            "Sicherheitscheck zurückgesetzt; keine Passwortwerte im UI-Zustand."
        )
        self.query_one("#status", Static).update(
            "[green]Ergebnisse aus der Oberfläche entfernt.[/green]"
        )

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
                f"[red]Länge muss {MIN_PASSWORD_LENGTH}–{MAX_PASSWORD_LENGTH} und Anzahl 1–{MAX_BATCH_COUNT} sein.[/red]"
            )
            return None

        return GenerationForm(
            password_length=password_length,
            password_count=password_count,
            charset=CharacterSet(str(charset_select.value)),
        )

    @work(thread=True, exclusive=True)
    def _generate_in_worker(self, form: GenerationForm) -> None:
        try:
            result, decision = self._generate_callback(
                form.password_count,
                form.password_length,
                form.charset,
                False,
                False,
                SessionProfiles(enabled=set()),
            )
        except Exception:
            self.call_from_thread(self._show_generation_error)
            return
        self.call_from_thread(self._show_generation_result, result, decision)

    @work(thread=True, exclusive=True)
    def _hash_demo_in_worker(self, form: GenerationForm) -> None:
        try:
            report = run_local_hash_demo(form.password_length, form.charset)
        except Exception:
            self.call_from_thread(self._show_hash_demo_error)
            return
        self.call_from_thread(self._show_hash_demo_result, report)

    def _show_generation_error(self) -> None:
        self.query_one("#generate", Button).disabled = False
        self.query_one("#status", Static).update(
            "[red]Die Erzeugung ist fehlgeschlagen. Bitte Eingaben prüfen.[/red]"
        )

    def _show_hash_demo_error(self) -> None:
        self.query_one("#hash-demo-button", Button).disabled = False
        self.query_one("#status", Static).update(
            "[red]Die lokale Hash-Demo ist fehlgeschlagen. Bitte Umgebung prüfen.[/red]"
        )

    def _show_hash_demo_result(self, report: LocalHashDemoReport) -> None:
        self.query_one("#hash-demo-button", Button).disabled = False
        self.query_one("#hash-demo", Static).update(report.as_text())
        self.query_one("#status", Static).update(
            "[green]Lokale Hash-Demo abgeschlossen; keine Werte wurden gespeichert.[/green]"
        )

    def _show_generation_result(self, result: GenerationResult, decision: BackendDecision) -> None:
        self.query_one("#generate", Button).disabled = False
        self._last_passwords = tuple(result.passwords)
        self.query_one("#copy", Button).disabled = not bool(self._last_passwords)
        self.query_one("#check", Button).disabled = not bool(self._last_passwords)
        self.query_one("#clear", Button).disabled = not bool(self._last_passwords)
        self.query_one("#security-check", Static).update("Noch kein Sicherheitscheck durchgeführt.")
        self.query_one("#status", Static).update(
            f"[green]{len(result.passwords)} Passwort/Passwörter lokal erzeugt.[/green]"
        )
        self.query_one("#backend", Static).update(
            f"Backend: {result.backend.value.upper()}\n{decision.reason}\n"
            "Erzeugung: direkter OS-CSPRNG-Policy-Pfad"
        )
        self.query_one("#results", Static).update(
            "Generierte Passwörter\n"
            + "\n".join(f"{index}: {value}" for index, value in enumerate(result.passwords, 1))
        )

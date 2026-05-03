"""
Rich-Based Terminal User Interface for Password Generator.

Provides interactive menus for password generation with real-time progress tracking.
Supports non-blocking GPU computation using threading.
"""

import time
import threading
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


class RichUI:
    """Terminal UI for password generation with Rich library."""

    def __init__(self, cuda_available: bool, device_name: str = ""):
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
        
        self.console = Console()
        self.cuda_available = cuda_available
        self.device_name = device_name
        self.computation_thread = None
        self.computation_result = None
        self.computation_error = None
        self.computation_time = 0.0

    def show_header(self) -> None:
        """Display application header with system status."""
        header_text = "🔐 GPU-ACCELERATED PASSWORD GENERATOR"
        
        status = "✅ GPU Ready" if self.cuda_available else "⚠️  CPU Mode (No GPU)"
        device_info = f"Device: {self.device_name}" if self.device_name else "CPU-only"
        
        self.console.print()
        self.console.print(
            Panel(
                f"{header_text}\n{status}\n{device_info}",
                style="bold cyan",
                expand=False
            )
        )
        self.console.print()

    def get_password_length(self) -> int:
        """
        Prompt user for password length.
        
        Returns:
            Password length (8-256).
        """
        while True:
            try:
                length_str = Prompt.ask(
                    "[yellow]Password length[/yellow]",
                    default="64",
                    console=self.console
                )
                length = int(length_str)
                if PasswordGenerator.validate_length(length):
                    return length
                else:
                    self.console.print(
                        "[red]✗ Length must be between 8 and 256.[/red]"
                    )
            except ValueError:
                self.console.print("[red]✗ Please enter a valid number.[/red]")

    def get_character_set(self) -> CharacterSet:
        """
        Prompt user for character set selection.
        
        Returns:
            CharacterSet enum value.
        """
        self.console.print()
        self.console.print("[bold]Character Set:[/bold]")
        self.console.print("  [cyan]1[/cyan] - Normal (letters + digits)")
        self.console.print("  [cyan]2[/cyan] - Complete (+ special symbols)")
        
        while True:
            try:
                choice = Prompt.ask(
                    "Select",
                    default="1",
                    console=self.console
                )
                return parse_charset_input(choice)
            except ValueError:
                self.console.print("[red]✗ Please enter 1 or 2.[/red]")

    def get_overkill_mode(self) -> bool:
        """
        Prompt user for Overkill Mode.
        
        Returns:
            True if Overkill Mode enabled, False otherwise.
        """
        self.console.print()
        overkill = Confirm.ask(
            "[bold]Enable Overkill Mode?[/bold] (slower, more entropy)",
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
                    "[yellow]Passwords to generate[/yellow]",
                    default="1",
                    console=self.console
                )
                count = int(count_str)
                if count >= 1:
                    return count
                else:
                    self.console.print("[red]✗ Must be at least 1.[/red]")
            except ValueError:
                self.console.print("[red]✗ Please enter a valid number.[/red]")

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
        execution_mode: str = "GPU"
    ) -> None:
        """
        Display generated passwords in a formatted table.
        
        Args:
            passwords: List of password strings
            execution_mode: "GPU" or "CPU" (for display)
        """
        self.console.print()
        
        # Create table
        table = Table(title="Generated Passwords", show_header=True)
        table.add_column("#", style="cyan", width=5)
        table.add_column("Password", style="bold green")
        
        for idx, pwd in enumerate(passwords, 1):
            table.add_row(str(idx), pwd)

        self.console.print(table)
        
        # Summary
        self.console.print()
        summary = f"[cyan]Generated {len(passwords)} password(s) in {self.computation_time:.2f}s ({execution_mode})[/cyan]"
        self.console.print(summary)

    def show_error(self, title: str, message: str) -> None:
        """
        Display an error message.
        
        Args:
            title: Error title
            message: Error details
        """
        self.console.print()
        self.console.print(
            Panel(
                message,
                title=f"❌ {title}",
                style="bold red",
                expand=False
            )
        )
        self.console.print()

    def show_fallback_notice(self) -> None:
        """Display notice that system fell back to CPU mode."""
        self.console.print(
            Panel(
                "GPU acceleration unavailable. Using CPU mode.",
                title="⚠️  Fallback to CPU",
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
            "[bold]Generate another?[/bold]",
            default=False,
            console=self.console
        )

    def show_goodbye(self) -> None:
        """Display exit message."""
        self.console.print()
        self.console.print(
            Panel(
                "Thank you for using Password Generator!",
                style="bold cyan",
                expand=False
            )
        )
        self.console.print()

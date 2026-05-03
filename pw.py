"""
GPU-Accelerated Password Generator

Main orchestrator combining GPU/CPU entropy generation with Rich TUI.
No artificial delays—all computation time is real hardware work.

Features:
- CUDA/GPU acceleration with automatic CPU fallback
- Interactive menu-driven interface
- Overkill Mode for enhanced entropy (5x iterations)
- Batch password generation
- Real-time progress tracking

Usage:
    python pw.py
"""

import sys
import time
from cuda_engine import get_cuda_engine
from cpu_engine import get_cpu_engine, CPUEngine
from password_engine import PasswordGenerator, CharacterSet
from tui import RichUI


class PasswordGeneratorApp:
    """Main application orchestrator."""

    def __init__(self):
        """Initialize application with CUDA detection."""
        self.cuda_engine = get_cuda_engine()
        self.cpu_engine = get_cpu_engine()
        
        cuda_available, device_name, error_msg = self.cuda_engine.get_status()
        self.cuda_available = cuda_available
        self.device_name = device_name
        self.error_msg = error_msg
        self.use_gpu = cuda_available
        
        self.ui = RichUI(cuda_available, device_name)

    def generate_with_mode(
        self,
        password_count: int,
        password_length: int,
        charset: CharacterSet,
        overkill: bool = False
    ) -> tuple:
        """
        Generate passwords using available hardware (GPU or CPU).
        
        Args:
            password_count: Number of passwords to generate
            password_length: Length of each password
            charset: Character set to use
            overkill: If True, use 5x iterations for more entropy
            
        Returns:
            (passwords_list, execution_mode_string)
        """
        # Determine iteration count
        base_iterations = 200000
        iterations = CPUEngine.scale_iterations_for_mode(
            base_iterations,
            overkill=overkill,
            multiplier=5.0
        )
        
        # Try GPU first
        if self.use_gpu:
            try:
                entropy = self.cuda_engine.gpu_entropy_pbkdf2(
                    iterations=iterations,
                    hash_length=64
                )
                
                if entropy:
                    passwords = PasswordGenerator.generate_batch(
                        entropy,
                        password_count,
                        password_length,
                        charset
                    )
                    return passwords, "GPU"
                    
            except Exception as e:
                self.ui.show_error(
                    "GPU Generation Failed",
                    f"Falling back to CPU mode.\n{str(e)}"
                )
                self.use_gpu = False
                self.ui.show_fallback_notice()
        
        # Fallback to CPU
        try:
            entropy = self.cpu_engine.cpu_entropy_pbkdf2(
                iterations=iterations,
                hash_length=64
            )
            passwords = PasswordGenerator.generate_batch(
                entropy,
                password_count,
                password_length,
                charset
            )
            return passwords, "CPU"
            
        except Exception as e:
            self.ui.show_error(
                "Password Generation Failed",
                f"Unable to generate passwords: {str(e)}"
            )
            return [], "ERROR"

    def run_interactive(self) -> None:
        """Run interactive password generation loop."""
        self.ui.show_header()
        
        while True:
            try:
                # Collect user input
                password_length = self.ui.get_password_length()
                charset = self.ui.get_character_set()
                overkill = self.ui.get_overkill_mode()
                password_count = self.ui.get_batch_count()
                
                # Generate with threaded progress
                def compute():
                    passwords, mode = self.generate_with_mode(
                        password_count,
                        password_length,
                        charset,
                        overkill
                    )
                    return passwords, mode
                
                passwords, exec_mode = self.ui.run_computation_threaded(
                    compute,
                    description="Generating entropy and deriving passwords..."
                )
                
                # Display results
                if passwords:
                    self.ui.display_passwords(passwords, exec_mode)
                
                # Ask to continue
                if not self.ui.prompt_continue():
                    self.ui.show_goodbye()
                    break
                    
            except KeyboardInterrupt:
                self.ui.console.print("\n[yellow]Interrupted by user.[/yellow]")
                self.ui.show_goodbye()
                break
            except Exception as e:
                self.ui.show_error("Unexpected Error", str(e))

    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            self.run_interactive()
            return 0
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            return 1


def main():
    """Main entry point."""
    app = PasswordGeneratorApp()
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
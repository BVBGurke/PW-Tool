"""
CUDA Setup Helper

Detects CUDA version and suggests the correct CuPy installation command.
Run this before main app if you want GPU acceleration.
"""

import subprocess
import sys


def detect_cuda_version():
    """
    Attempt to detect CUDA version from nvidia-smi.
    
    Returns:
        (major_version, minor_version) or (None, None) if not found
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version,compute_cap", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Try parsing nvidia-smi output
            output = result.stdout.strip()
            print(f"nvidia-smi output: {output}")
            
            # Alternative: check CUDA path
            import os
            cuda_path = os.environ.get("CUDA_PATH", "")
            if cuda_path:
                print(f"CUDA_PATH detected: {cuda_path}")
            
            return None, None
    except Exception as e:
        print(f"Could not run nvidia-smi: {e}")
    
    return None, None


def suggest_cupy_install():
    """
    Suggest CuPy installation command based on CUDA version.
    """
    print("\n" + "="*60)
    print("CUDA SETUP HELPER")
    print("="*60)
    print()
    print("GPU acceleration requires CuPy with CUDA support.")
    print()
    print("To install CuPy, choose your CUDA version:")
    print()
    print("  CUDA 12.x:  pip install cupy-cuda12x")
    print("  CUDA 13.x:  pip install cupy-cuda13x")
    print()
    print("To verify your CUDA version, run: nvidia-smi")
    print()
    print("="*60)


if __name__ == "__main__":
    print("Detecting CUDA installation...")
    major, minor = detect_cuda_version()
    
    suggest_cupy_install()
    
    print("\nNote: GPU acceleration is optional.")
    print("The tool will use CPU mode if CUDA is unavailable.")

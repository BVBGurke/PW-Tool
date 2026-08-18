"""
Quick Verification Script (Fast version for testing)

Tests core functionality quickly without extensive batch generation.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cuda_engine import get_cuda_engine
from cpu_engine import get_cpu_engine
from password_engine import PasswordGenerator, CharacterSet
from system_mix import SystemMixStatus, collect_system_mix


def test_basic_functionality():
    """Quick test of all modules."""
    print("\n" + "="*60)
    print("QUICK VERIFICATION - Basic Functionality")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: CPU Entropy
    print("\n[1] CPU Entropy Generation...")
    tests_total += 1
    try:
        cpu_engine = get_cpu_engine()
        entropy = cpu_engine.cpu_entropy_pbkdf2(iterations=10000, hash_length=64)
        if len(entropy) == 64:
            print("    PASS - 64 bytes generated")
            tests_passed += 1
        else:
            print(f"    FAIL - Expected 64 bytes, got {len(entropy)}")
    except Exception as e:
        print(f"    FAIL - {e}")
    
    # Test 2: Password Generation
    print("\n[2] Password Generation...")
    tests_total += 1
    try:
        password = PasswordGenerator.generate(entropy, 32, CharacterSet.NORMAL)
        if len(password) == 32 and all(c in PasswordGenerator.CHARS_NORMAL for c in password):
            print(f"    PASS - Generated: {password[:20]}...")
            tests_passed += 1
        else:
            print(f"    FAIL - Invalid password: {password}")
    except Exception as e:
        print(f"    FAIL - {e}")
    
    # Test 3: Batch Generation
    print("\n[3] Batch Password Generation (5 passwords)...")
    tests_total += 1
    try:
        passwords = PasswordGenerator.generate_batch(entropy, 5, 32, CharacterSet.COMPLETE)
        if len(passwords) == 5 and all(len(p) == 32 for p in passwords):
            unique = len(set(passwords))
            print(f"    PASS - Generated 5 passwords ({unique} unique)")
            tests_passed += 1
        else:
            print(f"    FAIL - Invalid batch")
    except Exception as e:
        print(f"    FAIL - {e}")
    
    # Test 4: CUDA Detection
    print("\n[4] CUDA/GPU Detection...")
    tests_total += 1
    try:
        cuda_engine = get_cuda_engine()
        available, device_name, error_msg = cuda_engine.get_status()
        if available:
            print(f"    PASS - GPU detected: {device_name}")
            tests_passed += 1
        else:
            print(f"    INFO - GPU not available (CPU fallback active)")
            print(f"           {error_msg[:70]}")
            tests_passed += 1  # Not a failure
    except Exception as e:
        print(f"    FAIL - {e}")
    
    # Test 5: Iteration Scaling
    print("\n[5] Iteration Scaling (Normal vs Overkill)...")
    tests_total += 1
    try:
        from cpu_engine import CPUEngine
        normal = CPUEngine.scale_iterations_for_mode(200000, overkill=False)
        overkill = CPUEngine.scale_iterations_for_mode(200000, overkill=True, multiplier=5.0)
        
        if normal == 200000 and overkill == 1000000:
            print(f"    PASS - Normal: {normal}, Overkill: {overkill} (5x multiplier)")
            tests_passed += 1
        else:
            print(f"    FAIL - Expected 200k/1M, got {normal}/{overkill}")
    except Exception as e:
        print(f"    FAIL - {e}")
    
    # Test 6: Character Set Selection
    print("\n[6] Character Set Validation...")
    tests_total += 1
    try:
        normal_chars = PasswordGenerator.get_character_set(CharacterSet.NORMAL)
        complete_chars = PasswordGenerator.get_character_set(CharacterSet.COMPLETE)
        
        if len(normal_chars) == 62 and len(complete_chars) == 80:
            print(f"    PASS - Normal: {len(normal_chars)} chars, Complete: {len(complete_chars)} chars")
            tests_passed += 1
        else:
            print(f"    FAIL - Expected Normal: 62, Complete: 80; got {len(normal_chars)}, {len(complete_chars)}")
    except Exception as e:
        print(f"    FAIL - {e}")
    
    # Test 7: Automatic local system mix
    print("\n[7] Automatic Local System Mix...")
    tests_total += 1
    try:
        system_mix = collect_system_mix(enabled=True)
        if system_mix.status is SystemMixStatus.COMPLETE and system_mix.source_count in range(3, 6):
            mixed_entropy = cpu_engine.cpu_entropy_pbkdf2(
                iterations=10000,
                hash_length=64,
                system_mix=system_mix,
            )
            if len(mixed_entropy) == 64:
                print(f"    PASS - Complete local mix with {system_mix.source_count} sources")
                tests_passed += 1
            else:
                print("    FAIL - Mixed entropy has unexpected length")
        elif system_mix.status in (SystemMixStatus.PARTIAL, SystemMixStatus.UNAVAILABLE):
            print(f"    PASS - Safe fallback status: {system_mix.status.value}")
            tests_passed += 1
        else:
            print(f"    FAIL - Unexpected system mix status: {system_mix.status.value}")
    except Exception as e:
        print(f"    FAIL - {e}")

    # Summary
    print("\n" + "="*60)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    print("="*60)
    
    if tests_passed == tests_total:
        print("\n[SUCCESS] All verification tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {tests_total - tests_passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = test_basic_functionality()
    sys.exit(exit_code)

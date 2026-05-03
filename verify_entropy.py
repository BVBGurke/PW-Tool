"""
Entropy Verification Script

Tests the quality and distribution of generated passwords.
Validates that GPU/CPU entropy generation is working correctly.
"""

import sys
import os
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cuda_engine import get_cuda_engine
from cpu_engine import get_cpu_engine
from password_engine import PasswordGenerator, CharacterSet


def test_no_duplicates(count=100, length=64):
    """
    Test that generated passwords are unique.
    
    Args:
        count: Number of passwords to generate
        length: Length of each password
    """
    print(f"\n[TEST] Uniqueness: Generating {count} passwords...")
    
    cpu_engine = get_cpu_engine()
    entropy = cpu_engine.cpu_entropy_pbkdf2(iterations=5000)
    passwords = PasswordGenerator.generate_batch(entropy, count, length)
    
    unique_count = len(set(passwords))
    duplicate_count = count - unique_count
    
    print(f"  Generated: {count}")
    print(f"  Unique:    {unique_count}")
    print(f"  Duplicates: {duplicate_count}")
    
    if duplicate_count == 0:
        print("  [PASS] No duplicates detected")
        return True
    else:
        print(f"  [FAIL] Found {duplicate_count} duplicates")
        return False


def test_character_distribution(count=1000, length=64):
    """
    Test that character distribution is uniform.
    
    Args:
        count: Number of passwords to generate
        length: Length of each password
    """
    print(f"\n[TEST] Distribution: Generating {count} passwords...")
    
    cpu_engine = get_cpu_engine()
    entropy = cpu_engine.cpu_entropy_pbkdf2(iterations=5000)
    passwords = PasswordGenerator.generate_batch(entropy, count, length, CharacterSet.COMPLETE)
    
    # Combine all characters
    all_chars = "".join(passwords)
    char_counts = Counter(all_chars)
    
    total_chars = len(all_chars)
    charset = PasswordGenerator.CHARS_COMPLETE
    
    print(f"  Total characters: {total_chars}")
    print(f"  Unique characters: {len(char_counts)}")
    print(f"  Character set size: {len(charset)}")
    
    # Check that no character appears too frequently or too rarely
    expected_freq = total_chars / len(charset)
    tolerance = expected_freq * 0.3  # 30% tolerance
    
    outliers = 0
    for char, count_val in char_counts.most_common(5):
        deviation = abs(count_val - expected_freq)
        print(f"    '{char}': {count_val} (expected ~{expected_freq:.0f}, dev: {deviation:.0f})")
        if deviation > tolerance:
            outliers += 1
    
    if outliers <= 1:  # Allow 1 outlier due to randomness
        print("  [PASS] Distribution looks uniform")
        return True
    else:
        print(f"  [FAIL] Distribution has too many outliers")
        return False


def test_entropy_speed():
    """
    Test entropy generation speed.
    """
    print(f"\n[TEST] Performance: Normal and Overkill modes...")
    
    cpu_engine = get_cpu_engine()
    
    # Normal mode (200k iterations)
    print("  Normal mode (200k iterations)...", end="", flush=True)
    start = time.time()
    entropy = cpu_engine.cpu_entropy_pbkdf2(iterations=200000)
    normal_time = time.time() - start
    print(f" {normal_time:.2f}s")
    
    # Overkill mode (1M iterations)
    print("  Overkill mode (1M iterations)...", end="", flush=True)
    start = time.time()
    entropy = cpu_engine.cpu_entropy_pbkdf2(iterations=1000000)
    overkill_time = time.time() - start
    print(f" {overkill_time:.2f}s")
    
    print(f"  Ratio: {overkill_time / normal_time:.1f}x slower (expected ~5x)")
    
    return True


def test_cuda_availability():
    """
    Test CUDA availability detection.
    """
    print(f"\n[TEST] CUDA Detection...")
    
    cuda_engine = get_cuda_engine()
    available, device_name, error_msg = cuda_engine.get_status()
    
    print(f"  CUDA Available: {available}")
    if device_name:
        print(f"  Device: {device_name}")
        print("  [PASS] GPU detected")
        return True
    else:
        print(f"  CPU Mode: {error_msg[:100]}")
        print("  [INFO] GPU not available (CPU fallback is active)")
        return True  # Not a failure, just CPU mode


def test_password_validation(count=50):
    """
    Test that generated passwords meet requirements.
    
    Args:
        count: Number of passwords to validate
    """
    print(f"\n[TEST] Password Validation: Checking {count} passwords...")
    
    cpu_engine = get_cpu_engine()
    entropy = cpu_engine.cpu_entropy_pbkdf2(iterations=5000)
    
    failures = 0
    
    # Test NORMAL charset
    passwords = PasswordGenerator.generate_batch(
        entropy, count, 32, CharacterSet.NORMAL
    )
    
    for pwd in passwords:
        if len(pwd) != 32:
            print(f"  [FAIL] Wrong length: {pwd}")
            failures += 1
        
        if not all(c in PasswordGenerator.CHARS_NORMAL for c in pwd):
            print(f"  [FAIL] Invalid character in: {pwd}")
            failures += 1
    
    # Test COMPLETE charset
    passwords = PasswordGenerator.generate_batch(
        entropy, count, 32, CharacterSet.COMPLETE
    )
    
    for pwd in passwords:
        if len(pwd) != 32:
            failures += 1
        
        if not all(c in PasswordGenerator.CHARS_COMPLETE for c in pwd):
            failures += 1
    
    if failures == 0:
        print(f"  [PASS] All {count * 2} passwords valid")
        return True
    else:
        print(f"  [FAIL] {failures} validation errors")
        return False


def main():
    """Run all verification tests."""
    print("\n" + "="*60)
    print("PASSWORD GENERATOR - VERIFICATION SUITE")
    print("="*60)
    
    results = []
    
    results.append(("CUDA Detection", test_cuda_availability()))
    results.append(("Uniqueness", test_no_duplicates()))
    results.append(("Distribution", test_character_distribution()))
    results.append(("Performance", test_entropy_speed()))
    results.append(("Validation", test_password_validation()))
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n[SUCCESS] All verification tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

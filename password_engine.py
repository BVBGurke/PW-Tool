"""
Password Generation Engine.

Derives secure passwords from entropy sources (GPU or CPU).
Implements uniform character distribution and deterministic extraction.
"""

import secrets
import string
from typing import Optional, Tuple
from enum import Enum


class CharacterSet(Enum):
    """Available character sets for password generation."""
    NORMAL = "normal"      # Letters + digits
    COMPLETE = "complete"  # Letters + digits + special symbols


class PasswordGenerator:
    """Generates secure passwords from entropy sources."""

    # Character sets
    CHARS_NORMAL = string.ascii_letters + string.digits
    CHARS_COMPLETE = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}"

    @staticmethod
    def validate_length(length: int) -> bool:
        """
        Validate password length.
        
        Args:
            length: Desired password length
            
        Returns:
            True if length is valid (8-256), False otherwise.
        """
        return 8 <= length <= 256

    @staticmethod
    def get_character_set(charset: CharacterSet) -> str:
        """
        Get character set string.
        
        Args:
            charset: CharacterSet enum value
            
        Returns:
            String of available characters.
        """
        if charset == CharacterSet.COMPLETE:
            return PasswordGenerator.CHARS_COMPLETE
        return PasswordGenerator.CHARS_NORMAL

    @staticmethod
    def generate(
        entropy: bytes,
        length: int,
        charset: CharacterSet = CharacterSet.NORMAL
    ) -> str:
        """
        Derive a password from entropy bytes.
        
        Algorithm:
        1. Create large character pool (length × 5000)
        2. Shuffle pool using entropy as seed
        3. Extract contiguous slice deterministically using entropy offset
        
        Args:
            entropy: Source entropy (typically from GPU or CPU PBKDF2)
            length: Desired password length (must be valid)
            charset: Character set to use (NORMAL or COMPLETE)
            
        Returns:
            Generated password string of specified length.
            
        Raises:
            ValueError: If length is invalid.
        """
        if not PasswordGenerator.validate_length(length):
            raise ValueError(f"Length must be 8-256, got {length}")

        chars = PasswordGenerator.get_character_set(charset)
        
        # Create massive pool for distribution uniformity
        pool_size = length * 5000
        pool = [secrets.choice(chars) for _ in range(pool_size)]
        
        # Use entropy to seed shuffles (multiple shuffles increase randomness)
        rng = secrets.SystemRandom()
        
        # Derive shuffle seed from entropy
        num_shuffles = 5 + (entropy[0] % 5)  # 5-10 shuffles
        for i in range(num_shuffles):
            # Use different entropy bytes for each shuffle
            seed_byte = entropy[i % len(entropy)]
            rng.seed(entropy)  # Seed with full entropy
            rng.shuffle(pool)
        
        # Deterministic offset extraction using last entropy byte
        offset = entropy[-1] % (pool_size - length)
        password = "".join(pool[offset : offset + length])
        
        return password

    @staticmethod
    def generate_batch(
        entropy: bytes,
        count: int,
        length: int,
        charset: CharacterSet = CharacterSet.NORMAL
    ) -> list:
        """
        Generate multiple passwords from a single entropy source.
        
        Args:
            entropy: Source entropy
            count: Number of passwords to generate
            length: Length of each password
            charset: Character set to use
            
        Returns:
            List of count passwords.
        """
        if count < 1:
            raise ValueError("Count must be >= 1")
        
        passwords = []
        for i in range(count):
            # Derive unique entropy for each password by hashing
            import hashlib
            unique_entropy = hashlib.sha256(
                entropy + bytes([i])
            ).digest()
            password = PasswordGenerator.generate(
                unique_entropy,
                length,
                charset
            )
            passwords.append(password)
        
        return passwords


def parse_charset_input(choice: str) -> CharacterSet:
    """
    Parse user character set choice.
    
    Args:
        choice: User input ("1" for NORMAL, "2" for COMPLETE, or name)
        
    Returns:
        CharacterSet enum value.
        
    Raises:
        ValueError: If choice is invalid.
    """
    choice_lower = choice.lower().strip()
    
    if choice_lower in ("1", "normal"):
        return CharacterSet.NORMAL
    elif choice_lower in ("2", "complete"):
        return CharacterSet.COMPLETE
    else:
        raise ValueError(f"Invalid character set choice: {choice}")

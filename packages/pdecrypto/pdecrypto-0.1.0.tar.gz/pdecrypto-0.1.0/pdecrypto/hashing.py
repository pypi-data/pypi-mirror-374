import hashlib
import hmac
import os

def derive_subkey(key: bytes, index: int, block_size: int, salt: bytes) -> bytes:
    """
    Derive a subkey for each block using HKDF-like construction.
    """
    index_bytes = index.to_bytes(8, "big")
    return hashlib.sha256(salt + key + index_bytes).digest()[:block_size]

def generate_iv(block_size: int = 16) -> bytes:
    """Generate a random IV for the message."""
    return os.urandom(block_size)

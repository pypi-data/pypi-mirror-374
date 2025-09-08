from .hashing import derive_subkey, generate_iv
from .utils import split_blocks, join_blocks, xor_bytes, derive_permutation, apply_permutation, reverse_permutation, pad, unpad
import hmac
import hashlib

BLOCK_SIZE = 16

def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """
    Encrypts using Position-Dependent Encryption (PDE).

    Encryption steps:
        1. Pad the message to multiples of BLOCK_SIZE.
        2. Split into blocks.
        3. For each block:
           - Derive a position-dependent subkey using SHA-256.
           - Derive a permutation of bytes.
           - XOR the block with the subkey.
           - Apply the permutation.
        4. Join all blocks.
        5. Prepend a random IV and append HMAC for authentication.

    Args:
        plaintext (bytes): The message to encrypt.
        key (bytes): Secret key (bytes) for encryption.

    Returns:
        bytes: Encrypted message including IV + ciphertext + HMAC tag.
    """
    iv = generate_iv(BLOCK_SIZE)
    padded = pad(plaintext, BLOCK_SIZE)
    blocks = split_blocks(padded, BLOCK_SIZE)
    ciphertext_blocks = []

    for i, block in enumerate(blocks):
        subkey = derive_subkey(key, i, BLOCK_SIZE, iv)
        perm = derive_permutation(subkey, BLOCK_SIZE)
        mixed = xor_bytes(block, subkey)
        permuted = apply_permutation(mixed, perm)
        ciphertext_blocks.append(permuted)

    ciphertext = join_blocks(ciphertext_blocks)
    tag = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
    return iv + ciphertext + tag


def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """
    Decrypt ciphertext using Position-Dependent Encryption (PDE).

    Args:
        ciphertext (bytes): Encrypted message with IV + HMAC.
        key (bytes): Secret key (bytes) used for encryption.

    Returns:
        bytes: Decrypted original plaintext.

    Raises:
        ValueError: If HMAC authentication fails (message tampering detected).
    """
    iv = ciphertext[:BLOCK_SIZE]
    tag = ciphertext[-32:]
    ciphertext_body = ciphertext[BLOCK_SIZE:-32]

    expected_tag = hmac.new(key, iv + ciphertext_body, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Authentication failed")

    blocks = split_blocks(ciphertext_body, BLOCK_SIZE)
    plaintext_blocks = []

    for i, block in enumerate(blocks):
        subkey = derive_subkey(key, i, BLOCK_SIZE, iv)
        perm = derive_permutation(subkey, BLOCK_SIZE)
        unpermuted = reverse_permutation(block, perm)
        plain = xor_bytes(unpermuted, subkey)
        plaintext_blocks.append(plain)

    padded_plaintext = join_blocks(plaintext_blocks)
    return unpad(padded_plaintext)

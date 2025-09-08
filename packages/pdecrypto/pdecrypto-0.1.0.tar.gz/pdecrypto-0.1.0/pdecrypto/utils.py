import struct


def split_blocks(data: bytes, block_size: int):
    """Split data into blocks of given size, pad with zeros if needed."""
    blocks = []
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        if len(block) < block_size:
            block = block.ljust(block_size, b"\x00")
        blocks.append(block)
    return blocks


def join_blocks(blocks):
    """Join list of blocks into a single byte string."""
    return b"".join(blocks)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings."""
    return bytes(x ^ y for x, y in zip(a, b))


def derive_permutation(subkey: bytes, block_size: int):
    """Generate a permutation of block indices based on subkey."""
    indices = list(range(block_size))
    for i, b in enumerate(subkey):
        j = (i + b) % block_size
        indices[i % block_size], indices[j] = indices[j], indices[i % block_size]
    return indices


def apply_permutation(block: bytes, perm):
    """Permute bytes of block according to perm."""
    return bytes(block[i] for i in perm)


def reverse_permutation(block: bytes, perm):
    """Reverse a permutation."""
    out = bytearray(len(block))
    for i, p in enumerate(perm):
        out[p] = block[i]
    return bytes(out)

def pad(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > len(data):
        raise ValueError("Invalid padding")
    return data[:-pad_len]

# PDECrypto

Position-Dependent Encryption (PDE) library in Python.

## Security Notice
This library is **educational** and **custom encryption**.  
It is **not** a replacement for AES, ChaCha20, or other vetted cryptography.  
For real-world security, always use standardized and audited algorithms like AES-GCM or ChaCha20-Poly1305.

## Installation

Requires Python >= 3.7

# Install for development
pip install -e .

# Install from PyPI
pip install pdecrypto


## Usage

```python
from pdecrypto import encrypt, decrypt

key = b"supersecretkey1234567890"

# Encrypt a file
with open("example.png", "rb") as f:
    data = f.read()
ciphertext = encrypt(data, key)
with open("example.enc", "wb") as f:
    f.write(ciphertext)

# Decrypt
with open("example.enc", "rb") as f:
    encrypted_data = f.read()
plaintext = decrypt(encrypted_data, key)
with open("example_decrypted.png", "wb") as f:
    f.write(plaintext)
```

## Features

- Block-based encryption (16 bytes per block)
- Position-dependent subkeys
- Byte permutation per block
- HMAC authentication
- PKCS#7-style padding

## Testing

Run automated tests using unittest:

```
python -m unittest pdecrypto.tests.test_automated
```

Or discover all tests in the tests folder:

```
python -m unittest discover -s pdecrypto/tests
```

## Documentation

Each function in the library has docstrings describing:

- Purpose
- Arguments
- Return values
- Exceptions

Example:

```
def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """
    Encrypt a plaintext message using PDE.

    Args:
        plaintext (bytes): Message to encrypt.
        key (bytes): Secret key for encryption.

    Returns:
        bytes: Ciphertext including IV + HMAC tag.

    Raises:
        ValueError: If encryption fails.
    """
```

References:

| Function    | Description                       |
| ----------- | --------------------------------- |
| encrypt     | Encrypt bytes or files with a key |
| decrypt     | Decrypt ciphertext with a key     |
| BLOCK\_SIZE | Default block size (16 bytes)     |

## Security Notice

This library is for **educational purposes only**. It implements a custom encryption scheme called Position-Dependent Encryption (PDE) and is **not intended for real-world security**. 

Limitations:

- Not resistant to **side-channel attacks** (timing, memory, cache analysis, etc.).
- Tampering detection via HMAC is included, but the library **cannot guarantee full integrity or authenticity** in adversarial conditions.
- Custom algorithms like PDE have **not been audited** and may contain unknown vulnerabilities.

For real-world encryption, always use **standardized and audited cryptography** such as:

- AES-GCM  
- ChaCha20-Poly1305  

Do **not** use this library for sensitive or production data.


## Contributing

Feel free to submit pull requests or issues.  
Ensure all tests pass before contributing.

## License

MIT License (or your preferred license)

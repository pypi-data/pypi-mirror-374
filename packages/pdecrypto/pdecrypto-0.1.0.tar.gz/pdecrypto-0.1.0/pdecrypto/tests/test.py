import os
import unittest
from pdecrypto import encrypt, decrypt
from pdecrypto.core import BLOCK_SIZE

class TestPDEFull(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = b"supersecretkey1234567890"
        # Paths for image test
        cls.script_dir = os.path.dirname(os.path.abspath(__file__))
        cls.image_input = os.path.join(cls.script_dir, "test.png")
        cls.image_encrypted = os.path.join(cls.script_dir, "test.enc")
        cls.image_decrypted = os.path.join(cls.script_dir, "test_decrypted.png")
        # Check if test image exists
        if not os.path.isfile(cls.image_input):
            cls.image_exists = False
            print("⚠️ test.png not found, skipping image test")
        else:
            cls.image_exists = True

    def test_basic_encryption(self):
        msg = b"Hello World!"
        self.assertEqual(decrypt(encrypt(msg, self.key), self.key), msg)

    def test_empty_message(self):
        msg = b""
        self.assertEqual(decrypt(encrypt(msg, self.key), self.key), msg)

    def test_large_message(self):
        msg = b"A" * 10_000
        self.assertEqual(decrypt(encrypt(msg, self.key), self.key), msg)

    def test_all_zero_bytes(self):
        msg = bytes([0] * BLOCK_SIZE * 4)
        self.assertEqual(decrypt(encrypt(msg, self.key), self.key), msg)

    def test_all_255_bytes(self):
        msg = bytes([255] * BLOCK_SIZE * 4)
        self.assertEqual(decrypt(encrypt(msg, self.key), self.key), msg)

    def test_tampering_detection(self):
        msg = b"Tampering test"
        ciphertext = bytearray(encrypt(msg, self.key))
        ciphertext[BLOCK_SIZE] ^= 0xFF  # flip a byte
        with self.assertRaises(ValueError):
            decrypt(bytes(ciphertext), self.key)

    def test_image_encryption(self):
        if not self.image_exists:
            self.skipTest("test.png not found, skipping image test")
        # Read image
        with open(self.image_input, "rb") as f:
            image_data = f.read()
        # Encrypt and save
        ciphertext = encrypt(image_data, self.key)
        with open(self.image_encrypted, "wb") as f:
            f.write(ciphertext)
        # Decrypt and save
        decrypted_data = decrypt(ciphertext, self.key)
        with open(self.image_decrypted, "wb") as f:
            f.write(decrypted_data)
        # Verify bitwise equality
        self.assertEqual(image_data, decrypted_data)

if __name__ == "__main__":
    unittest.main()

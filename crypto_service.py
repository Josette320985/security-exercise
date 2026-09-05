import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config import Config

class CryptoService:
    def __init__(self):
        self.key = base64.urlsafe_b64decode(Config.DB_ENCRYPTION_KEY)
        if len(self.key) != 32:
            raise ValueError("Encryption key must decode to exactly 32 bytes")
        self.aes = AESGCM(self.key)

    @staticmethod
    def md5(value: str) -> str:
        return hashlib.md5(value.encode()).hexdigest()

    @staticmethod
    def sha256(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def encrypt(self, value: str) -> str:
        nonce = os.urandom(12)
        ciphertext = self.aes.encrypt(nonce, value.encode(), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()

    def decrypt(self, value: str) -> str:
        raw = base64.urlsafe_b64decode(value)
        nonce = raw[:12]
        ciphertext = raw[12:]
        plaintext = self.aes.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
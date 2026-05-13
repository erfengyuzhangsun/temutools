import os
from cryptography.fernet import Fernet


class CryptoUtils:
    _instance = None
    _cipher = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            key = os.environ.get("ENCRYPTION_KEY")
            if key:
                cls._cipher = Fernet(key.encode() if isinstance(key, str) else key)
            else:
                generated = Fernet.generate_key()
                os.environ["ENCRYPTION_KEY"] = generated.decode()
                cls._cipher = Fernet(generated)
        return cls._instance

    def encrypt(self, plain_text: str) -> str:
        if not plain_text:
            return ""
        return self._cipher.encrypt(plain_text.encode()).decode()

    def decrypt(self, cipher_text: str) -> str:
        if not cipher_text:
            return ""
        return self._cipher.decrypt(cipher_text.encode()).decode()

    @staticmethod
    def mask_sensitive(value: str, visible_chars: int = 4) -> str:
        if not value or len(value) <= visible_chars * 2:
            return value
        return value[:visible_chars] + "*" * (len(value) - visible_chars * 2) + value[-visible_chars:]

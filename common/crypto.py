import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


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
                raise RuntimeError(
                    "环境变量 ENCRYPTION_KEY 未设置。\n"
                    "请设置一个 Fernet 兼容的32字节加密密钥:\n"
                    f"  密钥生成: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"\n"
                    "  设置方式: export ENCRYPTION_KEY='生成的密钥'"
                )
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

import os
import hashlib
import base64
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# 应用固定签名，用于派生默认加密密钥
# 确保即使没有 ENCRYPTION_KEY 环境变量，密钥也始终一致
_APP_SIGNATURE = b"temu_tools_default_key_v1_2026"


def _derive_default_key() -> bytes:
    hash_bytes = hashlib.sha256(_APP_SIGNATURE).digest()
    return base64.urlsafe_b64encode(hash_bytes)


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
                fallback = _derive_default_key()
                cls._cipher = Fernet(fallback)
                logger.warning(
                    "未设置 ENCRYPTION_KEY 环境变量，"
                    "使用确定性派生密钥（推荐在 Streamlit Secrets 中显式设置）"
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

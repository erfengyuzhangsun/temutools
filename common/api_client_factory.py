import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_client_cache = {}


def _has_real_credentials() -> bool:
    app_key = os.environ.get("TEMU_APP_KEY", "")
    app_secret = os.environ.get("TEMU_APP_SECRET", "")
    return bool(app_key and app_secret)


def get_api_client(shop_id: int, user_id: Optional[int] = None):
    cache_key = f"shop_{shop_id}"
    if cache_key in _client_cache:
        return _client_cache[cache_key]

    if _has_real_credentials():
        from common.temu_client import TemuApiClient
        client = TemuApiClient(shop_id=shop_id)
        logger.info(f"🔌 使用真实API客户端 | shop_id={shop_id}")
    else:
        from common.mock_temu_client import MockTemuApiClient
        client = MockTemuApiClient(shop_id=shop_id)
        logger.info(f"🧪 使用模拟API客户端 | shop_id={shop_id}（设置 TEMU_APP_KEY+TEMU_APP_SECRET 切换为真实模式）")

    _client_cache[cache_key] = client
    return client


def clear_client_cache():
    _client_cache.clear()


def is_mock_mode() -> bool:
    return not _has_real_credentials()

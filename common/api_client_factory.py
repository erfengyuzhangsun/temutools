import logging
from typing import Optional

logger = logging.getLogger(__name__)

_client_cache = {}


def _shop_has_credentials(shop_id: int) -> bool:
    try:
        from db import execute_query
        rows = execute_query(
            "SELECT cred_id FROM temu_shop_credentials WHERE shop_id = ?",
            (shop_id,), fetch=True,
        )
        return bool(rows)
    except Exception:
        return False


def get_api_client(shop_id: int, user_id: Optional[int] = None):
    cache_key = f"shop_{shop_id}"
    if cache_key in _client_cache:
        return _client_cache[cache_key]

    if _shop_has_credentials(shop_id):
        from common.temu_client import TemuApiClient
        client = TemuApiClient(shop_id=shop_id)
        logger.info(f"🔌 使用真实API客户端 | shop_id={shop_id}")
    else:
        from common.mock_temu_client import MockTemuApiClient
        client = MockTemuApiClient(shop_id=shop_id)
        logger.info(f"🧪 使用模拟API客户端 | shop_id={shop_id}（请先在「店铺管理」中绑定API凭证）")

    _client_cache[cache_key] = client
    return client


def clear_client_cache():
    _client_cache.clear()


def is_mock_mode() -> bool:
    return False

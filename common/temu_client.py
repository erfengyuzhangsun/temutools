import json
import logging
import os
import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass
from common.retry import async_retry, RetryConfig
from common.crypto import CryptoUtils

logger = logging.getLogger(__name__)

RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=5.0,
    backoff_factor=2.0,
    retryable_exceptions=(ConnectionError, TimeoutError, IOError),
)


class TemuApiError(Exception):
    def __init__(self, message: str, status_code: int = 0, error_code: str = ""):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class TemuApiAuthError(TemuApiError):
    pass


class TemuApiTimeoutError(TemuApiError):
    pass


class TemuApiServerError(TemuApiError):
    pass


@dataclass
class TemuApiResponse:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200


class TemuApiClient:
    def __init__(self, shop_id: int, api_key: str = "", api_secret: str = ""):
        self.shop_id = shop_id
        self.base_url = "https://open-api.temu.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self._http_client = None
        self._proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        self._load_credentials_if_needed()

    def _load_credentials_if_needed(self):
        if self.api_key and self.api_secret:
            return
        try:
            from db import execute_query
            rows = execute_query(
                "SELECT encrypted_api_key, encrypted_api_secret FROM temu_shop_credentials "
                "WHERE shop_id = ?",
                (self.shop_id,), fetch=True,
            )
            if rows:
                from common.crypto import CryptoUtils
                crypto = CryptoUtils()
                self.api_key = crypto.decrypt(rows[0]["encrypted_api_key"])
                self.api_secret = crypto.decrypt(rows[0]["encrypted_api_secret"])
        except Exception:
            pass

    async def _ensure_client(self):
        if self._http_client is None:
            client_kwargs = {"timeout": 30.0}
            if self._proxy:
                client_kwargs["proxy"] = self._proxy
            self._http_client = httpx.AsyncClient(**client_kwargs)

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def _sign_request(self, params: dict) -> dict:
        signed = params.copy()
        signed["app_key"] = self.api_key
        signed["timestamp"] = self._get_timestamp()
        sign_str = self.api_secret + json.dumps(signed, sort_keys=True) + self.api_secret
        import hashlib
        signed["sign"] = hashlib.md5(sign_str.encode()).hexdigest().upper()
        return signed

    @staticmethod
    def _get_timestamp() -> str:
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    async def request(self, endpoint: str, method: str = "POST", params: dict = None) -> TemuApiResponse:
        await self._ensure_client()
        url = f"{self.base_url}{endpoint}"
        signed_params = await self._sign_request(params or {})

        try:
            if method.upper() == "GET":
                response = await self._http_client.get(url, params=signed_params)
            else:
                response = await self._http_client.post(url, json=signed_params)

            if response.status_code == 401:
                raise TemuApiAuthError(f"API认证失败(401)", status_code=401, error_code="AUTH_FAILED")
            elif response.status_code == 503:
                raise TemuApiServerError(f"服务器暂时不可用(503)", status_code=503, error_code="SERVICE_UNAVAILABLE")
            elif response.status_code >= 500:
                raise TemuApiServerError(
                    f"服务器错误({response.status_code})", status_code=response.status_code, error_code="SERVER_ERROR"
                )

            response.raise_for_status()
            result = response.json()
            return TemuApiResponse(success=True, data=result, status_code=response.status_code)

        except httpx.TimeoutException as e:
            raise TemuApiTimeoutError(f"请求超时: {str(e)}", status_code=0, error_code="TIMEOUT")
        except httpx.HTTPStatusError as e:
            raise TemuApiError(f"HTTP错误: {str(e)}", status_code=e.response.status_code)
        except (httpx.RequestError, ConnectionError) as e:
            error_msg = str(e)
            if "Name or service not known" in error_msg or "名称或服务未知" in error_msg:
                raise TemuApiError(
                    "无法连接 Temu API 服务器（DNS解析失败），请检查服务器网络配置",
                    status_code=0, error_code="DNS_ERROR"
                )
            raise TemuApiError(f"网络错误: {error_msg}", status_code=0, error_code="NETWORK_ERROR")

    @async_retry(RETRY_CONFIG)
    async def get_orders(self, page: int = 1, page_size: int = 500, **kwargs) -> TemuApiResponse:
        params = {
            "method": "temu.order.list.get",
            "page": page,
            "page_size": page_size,
            **kwargs
        }
        return await self.request("/api/open/order/list", params=params)

    @async_retry(RETRY_CONFIG)
    async def get_order_detail(self, order_id: str) -> TemuApiResponse:
        params = {
            "method": "temu.order.detail.get",
            "order_id": order_id,
        }
        return await self.request("/api/open/order/detail", params=params)

    @async_retry(RETRY_CONFIG)
    async def get_inventory(self, sku_codes: list = None) -> TemuApiResponse:
        params = {
            "method": "temu.inventory.get",
            "sku_codes": json.dumps(sku_codes or []),
        }
        return await self.request("/api/open/inventory/get", params=params)

    @async_retry(RETRY_CONFIG)
    async def get_pricing_notices(self, page: int = 1, page_size: int = 50) -> TemuApiResponse:
        params = {
            "method": "temu.pricing.notice.list",
            "page": page,
            "page_size": page_size,
        }
        return await self.request("/api/open/pricing/notice/list", params=params)

    @async_retry(RETRY_CONFIG)
    async def accept_pricing(self, notice_id: str) -> TemuApiResponse:
        params = {
            "method": "temu.pricing.notice.accept",
            "notice_id": notice_id,
        }
        return await self.request("/api/open/pricing/notice/accept", params=params)

    @async_retry(RETRY_CONFIG)
    async def reject_pricing(self, notice_id: str, reason: str = "") -> TemuApiResponse:
        params = {
            "method": "temu.pricing.notice.reject",
            "notice_id": notice_id,
            "reason": reason,
        }
        return await self.request("/api/open/pricing/notice/reject", params=params)

    @async_retry(RETRY_CONFIG)
    async def get_settlements(self, date_from: str, date_to: str, page: int = 1) -> TemuApiResponse:
        params = {
            "method": "temu.settlement.list.get",
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
        }
        return await self.request("/api/open/settlement/list", params=params)

    @async_retry(RETRY_CONFIG)
    async def get_shop_metrics(self, date_from: str, date_to: str) -> TemuApiResponse:
        params = {
            "method": "temu.shop.metrics.get",
            "date_from": date_from,
            "date_to": date_to,
        }
        return await self.request("/api/open/shop/metrics", params=params)

    @async_retry(RETRY_CONFIG)
    async def get_activities(self, page: int = 1) -> TemuApiResponse:
        params = {
            "method": "temu.activity.list.get",
            "page": page,
        }
        return await self.request("/api/open/activity/list", params=params)

    @async_retry(RETRY_CONFIG)
    async def get_messages(self, page: int = 1, page_size: int = 50) -> TemuApiResponse:
        params = {
            "method": "temu.message.list.get",
            "page": page,
            "page_size": page_size,
        }
        return await self.request("/api/open/message/list", params=params)

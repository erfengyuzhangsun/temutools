import hashlib
import json
import logging
import os
import time
import httpx
from typing import Optional, Any
from dataclasses import dataclass
from common.retry import async_retry, RetryConfig

logger = logging.getLogger(__name__)

RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=5.0,
    backoff_factor=2.0,
    retryable_exceptions=(ConnectionError, TimeoutError, IOError, httpx.TimeoutException),
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


API_REGION_MAP = {
    "global": "https://openapi-b-global.temu.com",
    "us": "https://openapi-b-us.temu.com",
    "eu": "https://openapi-b-eu.temu.com",
}


class TemuApiClient:
    def __init__(self, shop_id: int, api_key: str = "", api_secret: str = ""):
        self.shop_id = shop_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = ""
        self._http_client = None
        self._proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        region = os.environ.get("TEMU_API_REGION", "global")
        self.base_url = API_REGION_MAP.get(region, API_REGION_MAP["global"])
        self._load_credentials_if_needed()

    def _load_credentials_if_needed(self):
        app_key = os.environ.get("TEMU_APP_KEY", "")
        app_secret = os.environ.get("TEMU_APP_SECRET", "")
        if app_key and app_secret:
            self.api_key = app_key
            self.api_secret = app_secret
        try:
            from db import execute_query
            rows = execute_query(
                "SELECT encrypted_api_key, encrypted_api_secret, encrypted_access_token "
                "FROM temu_shop_credentials WHERE shop_id = ?",
                (self.shop_id,), fetch=True,
            )
            if rows:
                from common.crypto import CryptoUtils
                crypto = CryptoUtils()
                if (not self.api_key or not self.api_secret) and rows[0]["encrypted_api_key"]:
                    self.api_key = crypto.decrypt(rows[0]["encrypted_api_key"])
                    self.api_secret = crypto.decrypt(rows[0]["encrypted_api_secret"])
                if rows[0].get("encrypted_access_token"):
                    self.access_token = crypto.decrypt(rows[0]["encrypted_access_token"])
        except Exception:
            pass

    async def _ensure_client(self):
        if self._http_client is None:
            client_kwargs = {"timeout": 60.0}
            if self._proxy:
                client_kwargs["proxy"] = self._proxy
            self._http_client = httpx.AsyncClient(**client_kwargs)

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    @staticmethod
    def _sign(params: dict, secret: str) -> str:
        sorted_params = dict(sorted(params.items()))
        sign_str = secret
        for key, value in sorted_params.items():
            if value is not None:
                sign_str += f"{key}{value}"
        sign_str += secret
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

    async def request(self, api_type: str, params: dict = None) -> TemuApiResponse:
        await self._ensure_client()
        body = {
            "type": api_type,
            "app_key": self.api_key,
            "access_token": self.access_token,
            "timestamp": round(time.time()),
            "data_type": "JSON",
        }
        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            body.update(filtered)
        body["sign"] = self._sign(body, self.api_secret)
        url = f"{self.base_url}/openapi/router"
        try:
            response = await self._http_client.post(url, json=body)
            if response.status_code == 401:
                raise TemuApiAuthError("API认证失败(401)，请检查 app_key 或 access_token", status_code=401, error_code="AUTH_FAILED")
            elif response.status_code == 403:
                raise TemuApiAuthError("API权限不足(403)，请检查 access_token 权限范围", status_code=403, error_code="FORBIDDEN")
            elif response.status_code == 503:
                raise TemuApiServerError("Temu服务器暂时不可用(503)", status_code=503, error_code="SERVICE_UNAVAILABLE")
            elif response.status_code >= 500:
                raise TemuApiServerError(f"Temu服务器错误({response.status_code})", status_code=response.status_code, error_code="SERVER_ERROR")
            response.raise_for_status()
            result = response.json()
            if isinstance(result, dict):
                api_success = result.get("success", False)
                error_code = result.get("errorCode", 0)
                error_msg = result.get("errorMsg", "")
                if not api_success and error_code != 0:
                    if error_code == 1000000:
                        api_success = True
                    else:
                        return TemuApiResponse(
                            success=False,
                            data=result,
                            error=error_msg or f"API错误码: {error_code}",
                            status_code=response.status_code,
                        )
                return TemuApiResponse(success=api_success, data=result, status_code=response.status_code)
            return TemuApiResponse(success=True, data=result, status_code=response.status_code)
        except httpx.TimeoutException as e:
            raise TemuApiTimeoutError(f"请求超时: {str(e)}", status_code=0, error_code="TIMEOUT")
        except httpx.HTTPStatusError as e:
            raise TemuApiError(f"HTTP错误: {str(e)}", status_code=e.response.status_code)
        except (httpx.RequestError, ConnectionError) as e:
            error_msg = str(e)
            if "Name or service not known" in error_msg or "名称或服务未知" in error_msg:
                raise TemuApiError(
                    "无法连接 Temu API 服务器(DNS解析失败)，请检查服务器网络配置",
                    status_code=0, error_code="DNS_ERROR",
                )
            raise TemuApiError(f"网络错误: {error_msg}", status_code=0, error_code="NETWORK_ERROR")

    def _extract_result(self, resp: TemuApiResponse) -> dict:
        if not resp.data:
            return {}
        if isinstance(resp.data, dict):
            return resp.data.get("result") or resp.data
        return resp.data

    @async_retry(RETRY_CONFIG)
    async def get_orders(self, page: int = 1, page_size: int = 100, **kwargs) -> TemuApiResponse:
        return await self.request("bg.order.list.v2.get", {
            "pageSize": page_size,
            "pageNumber": page,
            **kwargs,
        })

    @async_retry(RETRY_CONFIG)
    async def get_order_detail(self, parent_order_sn: str) -> TemuApiResponse:
        return await self.request("bg.order.detail.v2.get", {
            "parentOrderSn": parent_order_sn,
        })

    @async_retry(RETRY_CONFIG)
    async def get_inventory(self, sku_codes: list = None) -> TemuApiResponse:
        return await self.request("bg.local.goods.sku.list.query", {
            "skuIdList": json.dumps(sku_codes or [], ensure_ascii=False),
        })

    @async_retry(RETRY_CONFIG)
    async def get_pricing_notices(self, page: int = 1, page_size: int = 50) -> TemuApiResponse:
        raise TemuApiError("核价通知API(price notice)未在Temu开放平台公开接口中提供", status_code=0, error_code="API_NOT_AVAILABLE")

    @async_retry(RETRY_CONFIG)
    async def accept_pricing(self, notice_id: str) -> TemuApiResponse:
        raise TemuApiError("接受核价API(price accept)未在Temu开放平台公开接口中提供", status_code=0, error_code="API_NOT_AVAILABLE")

    @async_retry(RETRY_CONFIG)
    async def reject_pricing(self, notice_id: str, reason: str = "") -> TemuApiResponse:
        raise TemuApiError("拒绝核价API(price reject)未在Temu开放平台公开接口中提供", status_code=0, error_code="API_NOT_AVAILABLE")

    @async_retry(RETRY_CONFIG)
    async def get_settlements(self, date_from: str, date_to: str, page: int = 1) -> TemuApiResponse:
        raise TemuApiError("结算查询API(settlement)未在Temu开放平台公开接口中提供", status_code=0, error_code="API_NOT_AVAILABLE")

    @async_retry(RETRY_CONFIG)
    async def get_shop_metrics(self, date_from: str, date_to: str) -> TemuApiResponse:
        raise TemuApiError("店铺指标API(metrics)未在Temu开放平台公开接口中提供", status_code=0, error_code="API_NOT_AVAILABLE")

    @async_retry(RETRY_CONFIG)
    async def get_messages(self, page: int = 1, page_size: int = 50) -> TemuApiResponse:
        raise TemuApiError("消息列表API(message)未在Temu开放平台公开接口中提供", status_code=0, error_code="API_NOT_AVAILABLE")

    @async_retry(RETRY_CONFIG)
    async def get_activities(self, page: int = 1) -> TemuApiResponse:
        return await self.request("bg.promotion.activity.query", {
            "pageNumber": page,
            "pageSize": 20,
        })

    @async_retry(RETRY_CONFIG)
    async def get_access_token(self, code: str) -> TemuApiResponse:
        return await self.request("bg.open.accesstoken.create", {
            "code": code,
        })

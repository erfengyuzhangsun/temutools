import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
from modules.api_sync.schemas import (
    ServiceResult, SyncResult, SyncStatus, SyncType,
    SyncRecord, SyncHistoryItem, ShopBindRequest, ShopInfo,
)
from modules.api_sync.config import MODULE_CONFIG
from common.temu_client import (
    TemuApiClient, TemuApiAuthError, TemuApiTimeoutError,
    TemuApiServerError, TemuApiError,
)
from common.crypto import CryptoUtils

logger = logging.getLogger(__name__)


class ApiSyncService:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.crypto = CryptoUtils()

    async def sync_orders(
        self, shop_id: int, page_size: int = None, sync_type: SyncType = SyncType.ORDER
    ) -> SyncResult:
        start_time = time.time()
        logger.info(f"开始同步订单 | user_id={self.user_id} | shop_id={shop_id}")

        if page_size is None:
            page_size = MODULE_CONFIG["page_size"]["default"]

        shop_credentials = self._get_shop_credentials(shop_id)
        if not shop_credentials:
            return SyncResult(
                success=False, message="店铺未绑定或API凭证缺失",
                error_code="SHOP_NOT_BOUND", sync_status=SyncStatus.FAILED,
                duration_seconds=time.time() - start_time,
            )

        client = TemuApiClient(
            shop_id=shop_id,
            api_key=shop_credentials["api_key"],
            api_secret=shop_credentials["api_secret"],
        )

        try:
            existing_ids = await self._get_existing_order_ids(shop_id)

            all_orders = []
            page = 1
            total_count = 0
            warnings = []

            while True:
                response = await client.get_orders(page=page, page_size=page_size)
                if not response.success:
                    return SyncResult(
                        success=False, message=response.error or "同步失败",
                        error_code="SYNC_ERROR", sync_status=SyncStatus.FAILED,
                        duration_seconds=time.time() - start_time,
                    )

                data = response.data or {}
                orders = data.get("orders", []) or []
                total_count = data.get("total", 0) or 0

                for order in orders:
                    missing_fields = self._validate_order_fields(order)
                    if missing_fields:
                        warnings.append(
                            f"订单{order.get('order_id', 'unknown')}缺失字段: {', '.join(missing_fields)}"
                        )

                    if order.get("order_id") not in existing_ids:
                        all_orders.append(order)

                if len(orders) < page_size:
                    break
                page += 1

            duplicate_count = len(existing_ids & {o.get("order_id") for o in orders if o.get("order_id")})
            synced_count = await self._batch_save_orders(shop_id, all_orders)

            await self._record_sync_history(
                shop_id=shop_id, sync_type=sync_type.value,
                status=SyncStatus.SUCCESS, synced_count=synced_count,
                record_count=len(all_orders),
                started_at=datetime.fromtimestamp(start_time),
                duration_seconds=time.time() - start_time,
            )

            duration = time.time() - start_time
            logger.info(
                f"订单同步完成 | shop_id={shop_id} | "
                f"新增={synced_count} | 去重={duplicate_count} | 耗时={duration:.2f}s"
            )

            return SyncResult(
                success=True, message=f"同步完成，新增{synced_count}条",
                sync_status=SyncStatus.SUCCESS,
                data={
                    "synced_count": synced_count,
                    "duplicate_skipped": duplicate_count,
                    "total_in_api": total_count,
                    "warnings": warnings,
                    "orders": all_orders,
                },
                duration_seconds=duration,
            )

        except TemuApiAuthError as e:
            logger.error(f"API认证失败 | shop_id={shop_id} | {e.message}")
            await self._record_sync_history(
                shop_id=shop_id, sync_type=sync_type.value,
                status=SyncStatus.FAILED, synced_count=0,
                error_message=e.message, duration_seconds=time.time() - start_time,
            )
            return SyncResult(
                success=False, message=e.message,
                error_code=e.error_code, sync_status=SyncStatus.FAILED,
                duration_seconds=time.time() - start_time,
            )

        except TemuApiTimeoutError as e:
            logger.error(f"API超时 | shop_id={shop_id} | {e.message}")
            await self._record_sync_history(
                shop_id=shop_id, sync_type=sync_type.value,
                status=SyncStatus.FAILED, synced_count=0,
                error_message=e.message, duration_seconds=time.time() - start_time,
            )
            return SyncResult(
                success=False, message=e.message,
                error_code=e.error_code, sync_status=SyncStatus.FAILED,
                duration_seconds=time.time() - start_time,
            )

        except TemuApiServerError as e:
            logger.error(f"API服务器错误 | shop_id={shop_id} | {e.message}")
            await self._record_sync_history(
                shop_id=shop_id, sync_type=sync_type.value,
                status=SyncStatus.FAILED, synced_count=0,
                error_message=e.message, duration_seconds=time.time() - start_time,
            )
            return SyncResult(
                success=False, message=e.message,
                error_code=e.error_code, sync_status=SyncStatus.FAILED,
                duration_seconds=time.time() - start_time,
            )

        except Exception as e:
            logger.exception(f"同步异常 | shop_id={shop_id} | {str(e)}")
            await self._record_sync_history(
                shop_id=shop_id, sync_type=sync_type.value,
                status=SyncStatus.FAILED, synced_count=0,
                error_message=str(e), duration_seconds=time.time() - start_time,
            )
            return SyncResult(
                success=False, message=f"系统错误: {str(e)}",
                error_code="INTERNAL_ERROR", sync_status=SyncStatus.FAILED,
                duration_seconds=time.time() - start_time,
            )

        finally:
            await client.close()

    async def sync_all_shops(self, shop_ids: List[int]) -> Dict[int, SyncResult]:
        results = {}
        for shop_id in shop_ids:
            try:
                result = await self.sync_orders(shop_id=shop_id)
                results[shop_id] = result
            except Exception as e:
                logger.error(f"店铺{shop_id}同步异常 | {str(e)}")
                results[shop_id] = SyncResult(
                    success=False, message=f"同步异常: {str(e)}",
                    sync_status=SyncStatus.FAILED,
                )
        return results

    async def bind_shop(self, request: ShopBindRequest) -> ServiceResult:
        try:
            encrypted_key = self.crypto.encrypt(request.api_key)
            encrypted_secret = self.crypto.encrypt(request.api_secret)

            shop_id = self._save_shop_to_db(
                user_id=self.user_id,
                shop_name=request.shop_name,
                encrypted_api_key=encrypted_key,
                encrypted_api_secret=encrypted_secret,
                main_category=request.main_category,
            )

            logger.info(f"店铺绑定成功 | user_id={self.user_id} | shop_name={request.shop_name}")
            return ServiceResult(
                success=True, message="店铺绑定成功",
                data={"shop_id": shop_id, "encrypted_api_key": encrypted_key},
            )

        except Exception as e:
            logger.error(f"店铺绑定失败 | {str(e)}")
            return ServiceResult(
                success=False, message=f"绑定失败: {str(e)}",
                error_code="BIND_FAILED",
            )

    async def get_sync_history(self, shop_id: int, limit: int = 20) -> List[SyncHistoryItem]:
        return await self._get_sync_history_from_db(shop_id, limit)

    async def get_all_orders(self, shop_id: int) -> List[dict]:
        return await self._query_orders_from_db(shop_id)

    def _get_shop_credentials(self, shop_id: int) -> Optional[dict]:
        try:
            shop_data = self._query_shop_credentials(shop_id)
            if not shop_data:
                return None
            return {
                "api_key": self.crypto.decrypt(shop_data["encrypted_api_key"]),
                "api_secret": self.crypto.decrypt(shop_data["encrypted_api_secret"]),
            }
        except Exception as e:
            logger.error(f"获取店铺凭证失败 | shop_id={shop_id} | {str(e)}")
            return None

    @staticmethod
    def _validate_order_fields(order: dict) -> List[str]:
        required_fields = [
            "order_id", "sku", "product_name", "category",
            "buyer_payment", "platform_shipping", "settlement_price",
            "cost_price", "status",
        ]
        missing = []
        for field in required_fields:
            if field not in order or order.get(field) is None:
                missing.append(field)
        return missing

    async def _get_existing_order_ids(self, shop_id: int) -> Set[str]:
        return self._query_existing_order_ids(shop_id)

    async def _batch_save_orders(self, shop_id: int, orders: List[dict]) -> int:
        return self._insert_orders_batch(shop_id, orders)

    async def _record_sync_history(
        self, shop_id: int, sync_type: str, status: SyncStatus,
        synced_count: int, record_count: int = 0,
        error_message: str = "", started_at: datetime = None,
        duration_seconds: float = 0.0,
    ):
        self._insert_sync_history(
            user_id=self.user_id, shop_id=shop_id, sync_type=sync_type,
            status=status.value, synced_count=synced_count,
            record_count=record_count, error_message=error_message,
            duration_seconds=duration_seconds,
        )

    async def _get_sync_history_from_db(self, shop_id: int, limit: int = 20) -> List[SyncHistoryItem]:
        return self._query_sync_history(self.user_id, shop_id, limit)

    async def _query_orders_from_db(self, shop_id: int) -> List[dict]:
        return self._select_orders(self.user_id, shop_id)

    def _query_shop_credentials(self, shop_id: int) -> Optional[dict]:
        from db import execute_query
        rows = execute_query(
            "SELECT encrypted_api_key, encrypted_api_secret FROM temu_shop_credentials "
            "WHERE user_id = ? AND shop_id = ?",
            (self.user_id, shop_id), fetch=True,
        )
        return rows[0] if rows else None

    def _save_shop_to_db(
        self, user_id: int, shop_name: str,
        encrypted_api_key: str, encrypted_api_secret: str,
        main_category: str,
    ) -> int:
        from db import execute_query
        from db import get_or_create_shop
        shop_id = get_or_create_shop(user_id, shop_name, main_category)
        execute_query(
            "INSERT OR REPLACE INTO temu_shop_credentials "
            "(user_id, shop_id, encrypted_api_key, encrypted_api_secret) "
            "VALUES (?, ?, ?, ?)",
            (user_id, shop_id, encrypted_api_key, encrypted_api_secret),
        )
        return shop_id

    def _query_existing_order_ids(self, shop_id: int) -> Set[str]:
        from db import execute_query
        rows = execute_query(
            "SELECT order_id FROM temu_sync_orders WHERE user_id = ? AND shop_id = ?",
            (self.user_id, shop_id), fetch=True,
        )
        return {row["order_id"] for row in rows} if rows else set()

    def _insert_orders_batch(self, shop_id: int, orders: List[dict]) -> int:
        from db import execute_query
        count = 0
        for order in orders:
            try:
                execute_query(
                    "INSERT OR IGNORE INTO temu_sync_orders "
                    "(user_id, shop_id, order_id, sku, product_name, category, "
                    "buyer_payment, platform_shipping, settlement_price, cost_price, "
                    "status, create_time, ship_time, confirm_time, return_status, store_score) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        self.user_id, shop_id,
                        order.get("order_id", ""),
                        order.get("sku", ""),
                        order.get("product_name", ""),
                        order.get("category", "家居百货"),
                        float(order.get("buyer_payment", 0)),
                        float(order.get("platform_shipping", 0)),
                        float(order.get("settlement_price", 0)),
                        float(order.get("cost_price", 0)),
                        order.get("status", "pending"),
                        order.get("create_time"),
                        order.get("ship_time"),
                        order.get("confirm_time"),
                        order.get("return_status", ""),
                        float(order.get("store_score", 4.8)),
                    ),
                )
                count += 1
            except Exception as e:
                logger.warning(f"插入订单失败 | order_id={order.get('order_id')} | {str(e)}")
        return count

    def _insert_sync_history(
        self, user_id: int, shop_id: int, sync_type: str,
        status: str, synced_count: int, record_count: int = 0,
        error_message: str = "", duration_seconds: float = 0.0,
    ):
        from db import execute_query
        execute_query(
            "INSERT INTO temu_sync_history "
            "(user_id, shop_id, sync_type, status, synced_count, record_count, "
            "error_message, duration_seconds) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, shop_id, sync_type, status, synced_count,
             record_count, error_message, duration_seconds),
        )

    def _query_sync_history(self, user_id: int, shop_id: int, limit: int = 20) -> List[SyncHistoryItem]:
        from db import execute_query
        rows = execute_query(
            "SELECT sync_id, shop_id, sync_type, status, synced_count, "
            "started_at, finished_at, duration_seconds, error_message, record_count "
            "FROM temu_sync_history WHERE user_id = ? AND shop_id = ? "
            "ORDER BY started_at DESC LIMIT ?",
            (user_id, shop_id, limit), fetch=True,
        )
        items = []
        for row in rows:
            try:
                started_at = row.get("started_at")
                if isinstance(started_at, str):
                    started_at = datetime.fromisoformat(started_at)
                finished_at = row.get("finished_at")
                if isinstance(finished_at, str):
                    finished_at = datetime.fromisoformat(finished_at)
            except (ValueError, TypeError):
                started_at = datetime.now()
                finished_at = None

            items.append(SyncHistoryItem(
                sync_id=row.get("sync_id", 0),
                shop_id=row.get("shop_id", shop_id),
                sync_type=row.get("sync_type", ""),
                status=SyncStatus(row.get("status", "pending")),
                synced_count=row.get("synced_count", 0),
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=float(row.get("duration_seconds", 0)),
                error_message=row.get("error_message", ""),
                record_count=row.get("record_count", 0),
            ))
        return items

    def _select_orders(self, user_id: int, shop_id: int) -> List[dict]:
        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_sync_orders WHERE user_id = ? AND shop_id = ?",
            (user_id, shop_id), fetch=True,
        )
        return rows or []

import logging
from datetime import datetime
from typing import List, Optional
from modules.pricing.schemas import (
    PricingResult, PricingAction, PricingLogItem, ServiceResult,
)
from modules.pricing.config import MODULE_CONFIG
from common.temu_client import TemuApiError
from common.api_client_factory import get_api_client

logger = logging.getLogger(__name__)


class PricingService:
    def __init__(self, user_id: int):
        from common.plan_guard import check_plan_access
        check_plan_access("pricing", user_id)
        self.user_id = user_id

    async def auto_handle_pricing(self, shop_id: int) -> ServiceResult:
        logger.info(f"开始自动核价处理 | user_id={self.user_id} | shop_id={shop_id}")

        client = get_api_client(shop_id=shop_id, user_id=self.user_id)

        try:
            page_size = MODULE_CONFIG["max_notices_per_page"]["default"]
            response = await client.get_pricing_notices(page=1, page_size=page_size)

            if not response.success:
                return ServiceResult(
                    success=False, message="获取核价通知失败",
                    error_code="FETCH_FAILED",
                )

            notices = (response.data or {}).get("notices", []) or []
            if not notices:
                return ServiceResult(
                    success=True, message="无待处理核价通知",
                    data={"handled_count": 0, "results": []},
                )

            profit_threshold = await self._get_profit_threshold(shop_id)
            activity_threshold = await self._get_activity_profit_threshold(shop_id)
            now = datetime.now()
            results = []
            expiring_soon = []

            for notice in notices:
                sku = notice.get("sku", "")
                supply_price = float(notice.get("supply_price", 0))
                is_activity = bool(notice.get("is_activity", False))
                notice_id = notice.get("notice_id", "")
                expire_at = notice.get("expire_at")

                cost_price = await self._get_cost_price(sku, shop_id)
                if cost_price is None or cost_price <= 0:
                    results.append(PricingResult(
                        notice_id=notice_id, sku=sku,
                        supply_price=supply_price, cost_price=0,
                        gross_margin=0, action=PricingAction.SKIP,
                        reason="成本价缺失，待人工处理",
                    ))
                    await self._save_pricing_log(
                        shop_id=shop_id, notice_id=notice_id, sku=sku,
                        action="skip", supply_price=supply_price,
                        cost_price=0, gross_margin=0,
                        reason="成本价缺失，待人工处理",
                    )
                    continue

                gross_margin = ((supply_price - cost_price) / cost_price) * 100
                threshold = activity_threshold if is_activity else profit_threshold

                if gross_margin >= threshold:
                    action = PricingAction.ACCEPT
                    reason = "毛利率达标，自动接受"
                    await client.accept_pricing(notice_id)
                else:
                    action = PricingAction.REJECT
                    reason = f"毛利率{gross_margin:.1f}%低于阈值{threshold:.0f}%，自动拒绝"
                    await client.reject_pricing(notice_id, reason)

                results.append(PricingResult(
                    notice_id=notice_id, sku=sku,
                    supply_price=supply_price, cost_price=cost_price,
                    gross_margin=round(gross_margin, 2), action=action,
                    reason=reason,
                ))

                await self._save_pricing_log(
                    shop_id=shop_id, notice_id=notice_id, sku=sku,
                    action=action.value, supply_price=supply_price,
                    cost_price=cost_price, gross_margin=round(gross_margin, 2),
                    reason=reason, is_activity=is_activity,
                )

                if expire_at:
                    try:
                        expire_dt = datetime.fromisoformat(expire_at)
                        if 0 < (expire_dt - now).total_seconds() < MODULE_CONFIG["expiry_reminder_hours"]["default"] * 3600:
                            expiring_soon.append({
                                "notice_id": notice_id, "sku": sku,
                                "expire_at": expire_at,
                            })
                    except (ValueError, TypeError):
                        pass

            return ServiceResult(
                success=True,
                message=f"核价处理完成，共{len(results)}条",
                data={
                    "handled_count": len(results),
                    "results": [r.__dict__ for r in results],
                    "expiring_soon": expiring_soon,
                },
            )

        except TemuApiError as e:
            logger.error(f"核价API错误 | {e.message}")
            error_code = e.error_code
            if not error_code:
                class_name = type(e).__name__
                if "Auth" in class_name:
                    error_code = "AUTH_FAILED"
                elif "Timeout" in class_name:
                    error_code = "TIMEOUT"
                elif "Server" in class_name:
                    error_code = "SERVER_ERROR"
                else:
                    error_code = "API_ERROR"
            return ServiceResult(
                success=False, message=e.message,
                error_code=error_code,
            )
        except Exception as e:
            logger.exception(f"核价处理异常 | {str(e)}")
            return ServiceResult(
                success=False, message=f"系统错误: {str(e)}",
                error_code="INTERNAL_ERROR",
            )
        finally:
            await client.close()

    async def get_pricing_logs(self, shop_id: int, limit: int = 50) -> List[PricingLogItem]:
        return await self._get_pricing_logs_from_db(shop_id, limit)

    async def _get_profit_threshold(self, shop_id: int) -> float:
        return float(MODULE_CONFIG["default_profit_threshold"]["default"])

    async def _get_activity_profit_threshold(self, shop_id: int) -> float:
        return float(MODULE_CONFIG["activity_profit_threshold"]["default"])

    async def _get_cost_price(self, sku: str, shop_id: int) -> Optional[float]:
        rows = self._query_cost_price(self.user_id, shop_id, sku)
        if rows:
            return float(rows[0]["cost_price"])
        return None

    async def _get_pricing_logs_from_db(self, shop_id: int, limit: int = 50) -> List[PricingLogItem]:
        return self._query_pricing_logs(self.user_id, shop_id, limit)

    async def _save_pricing_log(
        self, shop_id: int, notice_id: str, sku: str,
        action: str, supply_price: float, cost_price: float,
        gross_margin: float, reason: str = "", is_activity: bool = False,
    ):
        self._insert_pricing_log(
            user_id=self.user_id, shop_id=shop_id,
            notice_id=notice_id, sku=sku, action=action,
            supply_price=supply_price, cost_price=cost_price,
            gross_margin=gross_margin, reason=reason,
            is_activity=is_activity,
        )

    def _query_cost_price(self, user_id: int, shop_id: int, sku: str) -> list:
        from db import execute_query
        return execute_query(
            "SELECT cost_price FROM temu_sku_profit "
            "WHERE user_id = ? AND shop_id = ? AND sku_code = ?",
            (user_id, shop_id, sku), fetch=True,
        ) or []

    def _query_pricing_logs(self, user_id: int, shop_id: int, limit: int = 50) -> List[PricingLogItem]:
        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_pricing_logs "
            "WHERE user_id = ? AND shop_id = ? "
            "ORDER BY handled_at DESC LIMIT ?",
            (user_id, shop_id, limit), fetch=True,
        ) or []
        items = []
        for row in rows:
            handled_at = row.get("handled_at")
            if isinstance(handled_at, str):
                try:
                    handled_at = datetime.fromisoformat(handled_at)
                except (ValueError, TypeError):
                    handled_at = datetime.now()
            items.append(PricingLogItem(
                log_id=row.get("log_id", 0),
                notice_id=row.get("notice_id", ""),
                sku=row.get("sku", ""),
                action=row.get("action", ""),
                supply_price=float(row.get("supply_price", 0)),
                cost_price=float(row.get("cost_price", 0)),
                gross_margin=float(row.get("gross_margin", 0)),
                handled_at=handled_at,
                reason=row.get("reason", ""),
                is_activity=bool(row.get("is_activity", False)),
            ))
        return items

    def _insert_pricing_log(
        self, user_id: int, shop_id: int, notice_id: str, sku: str,
        action: str, supply_price: float, cost_price: float,
        gross_margin: float, reason: str = "", is_activity: bool = False,
    ):
        from db import execute_query
        execute_query(
            "INSERT INTO temu_pricing_logs "
            "(user_id, shop_id, notice_id, sku, action, supply_price, "
            "cost_price, gross_margin, reason, is_activity) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, shop_id, notice_id, sku, action,
             supply_price, cost_price, gross_margin, reason, 1 if is_activity else 0),
        )

import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Callable, Awaitable, List, Optional

logger = logging.getLogger(__name__)

TASK_TEMPLATES = []


@dataclass
class TaskTemplate:
    task_id: str
    name: str
    description: str
    default_cron: str
    callback_factory: Callable[[int], Callable[[], Awaitable[None]]]


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []


async def _callback_auto_sync_orders(user_id: int):
    from modules.api_sync.service import ApiSyncService
    shops = _get_user_shops(user_id)
    if not shops:
        logger.info(f"[自动同步订单] user={user_id} 无已绑定店铺，跳过")
        return
    service = ApiSyncService(user_id)
    results = []
    for shop in shops:
        try:
            result = await service.sync_orders(shop_id=shop["shop_id"])
            results.append(f"{shop['shop_name']}: {'✅' if result.success else '❌'} {result.message}")
        except Exception as e:
            results.append(f"{shop['shop_name']}: ❌ {e}")
    logger.info(f"[自动同步订单] user={user_id} | {' | '.join(results)}")


async def _callback_auto_process_pricing(user_id: int):
    from modules.pricing.service import PricingService
    shops = _get_user_shops(user_id)
    if not shops:
        logger.info(f"[自动核价处理] user={user_id} 无已绑定店铺，跳过")
        return
    results = []
    for shop in shops:
        try:
            service = PricingService(user_id)
            result = await service.auto_handle_pricing(shop_id=shop["shop_id"])
            handled = (result.data or {}).get("handled_count", 0)
            results.append(f"{shop['shop_name']}: {'✅' if result.success else '❌'} {result.message} (处理{handled}条)")
        except Exception as e:
            results.append(f"{shop['shop_name']}: ❌ {e}")
    logger.info(f"[自动核价处理] user={user_id} | {' | '.join(results)}")


async def _callback_auto_sync_inventory(user_id: int):
    from modules.inventory.service import InventoryService
    shops = _get_user_shops(user_id)
    if not shops:
        logger.info(f"[自动库存同步] user={user_id} 无已绑定店铺，跳过")
        return
    results = []
    for shop in shops:
        try:
            service = InventoryService(user_id)
            result = await service.sync_inventory(shop_id=shop["shop_id"])
            results.append(f"{shop['shop_name']}: {'✅' if result.success else '❌'} {result.message}")
        except Exception as e:
            results.append(f"{shop['shop_name']}: ❌ {e}")
    logger.info(f"[自动库存同步] user={user_id} | {' | '.join(results)}")


async def _callback_auto_risk_check(user_id: int):
    from common.services_p2p3 import RiskInspectionService
    shops = _get_user_shops(user_id)
    if not shops:
        logger.info(f"[自动风控体检] user={user_id} 无已绑定店铺，跳过")
        return
    results = []
    for shop in shops:
        try:
            service = RiskInspectionService(user_id)
            result = await service.inspect_all_skus(shop_id=shop["shop_id"])
            violations = len((result.data or {}).get("violations", []))
            results.append(f"{shop['shop_name']}: {'✅' if result.success else '❌'} 违规{violations}项")
        except Exception as e:
            results.append(f"{shop['shop_name']}: ❌ {e}")
    logger.info(f"[自动风控体检] user={user_id} | {' | '.join(results)}")


async def _callback_auto_sync_reviews(user_id: int):
    from common.services_p2p3 import ReviewMonitorService
    shops = _get_user_shops(user_id)
    if not shops:
        logger.info(f"[自动差评同步] user={user_id} 无已绑定店铺，跳过")
        return
    results = []
    for shop in shops:
        try:
            service = ReviewMonitorService(user_id)
            result = await service.sync_new_reviews(shop_id=shop["shop_id"])
            synced = (result.data or {}).get("new_reviews_synced", 0)
            alerts = (result.data or {}).get("alert_count", 0)
            results.append(f"{shop['shop_name']}: {'✅' if result.success else '❌'} 同步{synced}条, 告警{alerts}条")
        except Exception as e:
            results.append(f"{shop['shop_name']}: ❌ {e}")
    logger.info(f"[自动差评同步] user={user_id} | {' | '.join(results)}")


TASK_TEMPLATES = [
    TaskTemplate(
        task_id="auto_sync_orders",
        name="自动同步订单",
        description="定时从 Temu API 同步所有店铺的最新订单数据，包括核价、结算等",
        default_cron="0 */6 * * *",
        callback_factory=lambda uid: lambda: _callback_auto_sync_orders(uid),
    ),
    TaskTemplate(
        task_id="auto_process_pricing",
        name="自动核价处理",
        description="自动检查并处理所有店铺的核价通知，根据毛利率阈值自动接受或拒绝",
        default_cron="0 */3 * * *",
        callback_factory=lambda uid: lambda: _callback_auto_process_pricing(uid),
    ),
    TaskTemplate(
        task_id="auto_sync_inventory",
        name="自动库存同步",
        description="定时同步所有店铺的库存数据，识别低库存和高库存SKU",
        default_cron="0 */4 * * *",
        callback_factory=lambda uid: lambda: _callback_auto_sync_inventory(uid),
    ),
    TaskTemplate(
        task_id="auto_risk_check",
        name="自动风控体检",
        description="定时对所有店铺SKU进行风控合规检查，发现敏感词和违规风险",
        default_cron="0 9 * * *",
        callback_factory=lambda uid: lambda: _callback_auto_risk_check(uid),
    ),
    TaskTemplate(
        task_id="auto_sync_reviews",
        name="自动差评同步",
        description="定时同步所有店铺的最新差评，识别高风险SKU并预警",
        default_cron="0 */8 * * *",
        callback_factory=lambda uid: lambda: _callback_auto_sync_reviews(uid),
    ),
]


def get_template_ids() -> List[str]:
    return [t.task_id for t in TASK_TEMPLATES]


def is_template_task(task_id: str) -> bool:
    return any(t.task_id == task_id for t in TASK_TEMPLATES)


def compute_next_run_seconds(cron_expression: str) -> Optional[float]:
    try:
        from croniter import croniter
        now = datetime.now()
        cron = croniter(cron_expression, now)
        next_time = cron.get_next(datetime)
        return (next_time - now).total_seconds()
    except (ValueError, KeyError, ImportError):
        return None


def is_task_due(cron_expression: str, last_run: Optional[datetime]) -> bool:
    if last_run is None:
        return True
    next_run_seconds = compute_next_run_seconds(cron_expression)
    if next_run_seconds is None:
        return False
    return next_run_seconds <= 0

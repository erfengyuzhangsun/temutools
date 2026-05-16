import logging, json
from datetime import datetime, timedelta
from typing import List, Optional
from modules.inventory.schemas import ServiceResult, InventoryItem, ReplenishmentSuggestion
from modules.inventory.config import MODULE_CONFIG
logger = logging.getLogger(__name__)

class InventoryService:
    def __init__(self, user_id: int):
        from common.plan_guard import check_plan_access
        check_plan_access("inventory", user_id)
        self.user_id = user_id

    async def sync_inventory(self, shop_id: int) -> ServiceResult:
        logger.info(f"同步库存 | user_id={self.user_id} | shop_id={shop_id}")
        client = None
        try:
            from common.temu_client import TemuApiClient
            client = TemuApiClient(shop_id=shop_id)
            resp = await client.get_inventory()
            if not resp.success: return ServiceResult(success=False, message="库存API同步失败", error_code="SYNC_FAILED")
            items = (resp.data or {}).get("inventory", []) or []
            count = 0
            for item in items:
                self._upsert_inventory(shop_id, item)
                count += 1
            return ServiceResult(success=True, message=f"同步完成，共{count}个SKU", data={"synced_count": count})
        except Exception as e:
            logger.error(f"库存同步异常: {e}")
            return ServiceResult(success=False, message="库存同步异常，请检查网络连接及API凭证配置", error_code="SYNC_ERROR")
        finally:
            if client: await client.close()

    async def check_inventory_alerts(self, shop_id: int) -> ServiceResult:
        items = self._get_all_inventory(shop_id)
        alerts = []
        for item in items:
            stock, safe = item["current_stock"], item["safety_stock"]
            sku = item["sku"]
            if stock <= 0:
                alerts.append({"sku": sku, "type": "out_of_stock", "msg": f"SKU {sku} 已缺货"})
                self._save_alert(shop_id, sku, "out_of_stock", f"SKU {sku} 已缺货")
            elif stock < safe:
                alerts.append({"sku": sku, "type": "low_stock", "msg": f"SKU {sku} 库存不足({stock}<{safe})"})
                self._save_alert(shop_id, sku, "low_stock", f"SKU {sku} 库存不足({stock}<{safe})")
        slow_moving_days = MODULE_CONFIG["slow_moving_days"]["default"]
        threshold_date = (datetime.now() - timedelta(days=slow_moving_days)).isoformat()
        slow_items = self._get_slow_moving(shop_id, threshold_date)
        for si in slow_items:
            alerts.append({"sku": si["sku"], "type": "slow_moving", "msg": f"SKU {si['sku']} 已滞销{slow_moving_days}天"})
            self._save_alert(shop_id, si["sku"], "slow_moving", f"SKU {si['sku']} 已滞销{slow_moving_days}天")
        return ServiceResult(success=True, data={"alerts": alerts, "alert_count": len(alerts)})

    async def generate_replenishment_suggestions(self, shop_id: int) -> ServiceResult:
        items = self._get_all_inventory(shop_id)
        suggestions = []
        for item in items:
            stock = item["current_stock"]; daily = float(item["daily_avg_sales"] or 0)
            lead = int(item["lead_time_days"] or MODULE_CONFIG["replenishment_lead_time_default"]["default"])
            safe = int(item["safety_stock"] or MODULE_CONFIG["safety_stock_days"]["default"])
            if daily <= 0: continue
            days_until_stockout = int(stock / daily) if daily > 0 else 999
            suggested = max(0, int(daily * lead + safe - stock))
            priority = "high" if days_until_stockout <= lead else ("medium" if days_until_stockout <= lead * 2 else "low")
            suggestions.append(ReplenishmentSuggestion(
                sku=item["sku"], product_name=item["product_name"],
                current_stock=stock, suggested_quantity=suggested,
                suggested_order_date=(datetime.now() + timedelta(days=max(0, days_until_stockout - lead))).strftime("%Y-%m-%d"),
                estimated_days_until_stockout=days_until_stockout,
                daily_avg_sales=daily, priority=priority,
            ))
        return ServiceResult(success=True, data={"suggestions": [s.__dict__ for s in suggestions], "count": len(suggestions)})

    async def identify_slow_moving(self, shop_id: int) -> ServiceResult:
        days = MODULE_CONFIG["slow_moving_days"]["default"]
        threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
        items = self._get_slow_moving(shop_id, threshold_date)
        return ServiceResult(success=True, data={"slow_moving_skus": items, "count": len(items)})

    def _upsert_inventory(self, shop_id: int, item: dict):
        from db import execute_query
        execute_query(
            "INSERT OR REPLACE INTO temu_inventory (user_id, shop_id, sku, product_name, category, current_stock, safety_stock, daily_avg_sales, lead_time_days, cost_price, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self.user_id, shop_id, item.get("sku",""), item.get("product_name",""), item.get("category",""),
             int(item.get("current_stock",0)), int(item.get("safety_stock",0)), float(item.get("daily_avg_sales",0)),
             int(item.get("lead_time_days",7)), float(item.get("cost_price",0)), item.get("status","normal")))

    def _get_all_inventory(self, shop_id: int) -> list:
        from db import execute_query
        return execute_query("SELECT * FROM temu_inventory WHERE user_id=? AND shop_id=?", (self.user_id, shop_id), fetch=True) or []

    def _get_slow_moving(self, shop_id: int, threshold_date: str) -> list:
        from db import execute_query
        return execute_query(
            "SELECT sku, product_name, current_stock FROM temu_inventory WHERE user_id=? AND shop_id=? AND daily_avg_sales<=0 AND current_stock>0",
            (self.user_id, shop_id), fetch=True) or []

    def _save_alert(self, shop_id: int, sku: str, alert_type: str, message: str):
        from db import execute_query
        execute_query("INSERT INTO temu_inventory_alerts (user_id, shop_id, sku, alert_type, message) VALUES (?,?,?,?,?)",
                      (self.user_id, shop_id, sku, alert_type, message))

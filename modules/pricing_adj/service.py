import logging; from datetime import datetime; from typing import List; from modules.pricing_adj.schemas import ServiceResult, PriceAdjustment; from modules.pricing_adj.config import MODULE_CONFIG; from common.api_client_factory import get_api_client; logger=logging.getLogger(__name__)

class PricingAdjustmentService:
    def __init__(self, user_id: int): self.user_id = user_id

    async def auto_adjust_price(self, shop_id: int, sku: str) -> ServiceResult:
        logger.info(f"自动调价 | user_id={self.user_id} | shop_id={shop_id} | sku={sku}")
        today_count = self._get_today_adjustment_count(shop_id)
        max_adj = MODULE_CONFIG["max_daily_adjustments"]["default"]
        if today_count >= max_adj:
            return ServiceResult(success=False,message=f"当日调价次数已达上限({max_adj}次)",error_code="RATE_LIMIT")
        current_price = self._get_current_price(shop_id, sku)
        if not current_price: return ServiceResult(success=False,message="SKU无当前售价",error_code="NO_PRICE")
        cost_price = self._get_cost_price(shop_id, sku)
        min_margin = MODULE_CONFIG["min_gross_margin"]["default"] / 100
        min_price = cost_price * (1 + min_margin) if cost_price and cost_price > 0 else current_price * 0.7
        competitor_price = self._get_competitor_price(sku)
        if competitor_price and competitor_price < current_price:
            new_price = max(min_price, competitor_price * (1 + MODULE_CONFIG["competitor_price_drop_ratio"]["default"] * 0.5))
            if abs(new_price - current_price) / current_price < 0.01:
                return ServiceResult(success=True,message="价格已为最优，无需调整",data={"sku":sku,"old_price":current_price,"new_price":current_price})
            self._save_adjustment(shop_id, sku, current_price, round(new_price,2), f"竞品降价跟进({competitor_price}→{new_price})")
            return ServiceResult(success=True,data={"sku":sku,"old_price":current_price,"new_price":round(new_price,2),"reason":"竞品降价跟进"})
        return ServiceResult(success=True,message="无需调整",data={"sku":sku,"old_price":current_price,"new_price":current_price})

    async def adjust_for_activity(self, shop_id: int, sku: str, activity_price: float) -> ServiceResult:
        current_price = self._get_current_price(shop_id, sku)
        if not current_price: return ServiceResult(success=False,message="SKU无当前售价")
        self._save_adjustment(shop_id, sku, current_price, activity_price, "活动价切换")
        return ServiceResult(success=True,data={"sku":sku,"old_price":current_price,"new_price":activity_price,"reason":"活动价已生效"})

    async def get_adjustment_logs(self, shop_id: int, limit: int = 50) -> ServiceResult:
        rows = self._query_adjustments(shop_id, limit)
        logs=[]
        for r in rows:
            logs.append({"adj_id":r.get("adj_id"),"sku":r.get("sku"),"old_price":float(r.get("old_price",0)),"new_price":float(r.get("new_price",0)),"reason":r.get("reason",""),"type":r.get("adjustment_type","auto"),"operator":r.get("operator","system"),"time":str(r.get("created_at",""))})
        return ServiceResult(success=True,data={"logs":logs,"count":len(logs)})

    def _get_current_price(self, shop_id: int, sku: str) -> float:
        from db import execute_query, DB_MODE
        rows=execute_query("SELECT settlement_price FROM temu_sync_orders WHERE user_id=? AND shop_id=? AND sku=? ORDER BY synced_at DESC LIMIT 1",(self.user_id,shop_id,sku),fetch=True)
        if not rows: return 0.0
        return float(rows[0].get("settlement_price",0))

    def _get_cost_price(self, shop_id: int, sku: str) -> float:
        from db import execute_query
        rows=execute_query("SELECT cost_price FROM temu_sku_profit WHERE user_id=? AND shop_id=? AND sku_code=?",(self.user_id,shop_id,sku),fetch=True)
        if not rows: return 0.0
        return float(rows[0].get("cost_price",0))

    def _get_competitor_price(self, sku: str) -> float:
        from db import execute_query
        rows=execute_query("SELECT price FROM temu_competitor_prices WHERE sku=? ORDER BY collected_at DESC LIMIT 1",(sku,),fetch=True)
        if not rows: return 0.0
        return float(rows[0].get("price",0))

    def _save_adjustment(self, shop_id: int, sku: str, old: float, new_p: float, reason: str):
        from db import execute_query
        execute_query("INSERT INTO temu_price_adjustments (user_id,shop_id,sku,old_price,new_price,reason) VALUES (?,?,?,?,?,?)",(self.user_id,shop_id,sku,old,new_p,reason))

    def _get_today_adjustment_count(self, shop_id: int) -> int:
        from db import execute_query
        today=datetime.now().strftime("%Y-%m-%d")
        rows=execute_query("SELECT COUNT(*) as cnt FROM temu_price_adjustments WHERE user_id=? AND shop_id=? AND date(created_at)=?",(self.user_id,shop_id,today),fetch=True)
        return rows[0]["cnt"] if rows else 0

    def _query_adjustments(self, shop_id: int, limit: int) -> list:
        from db import execute_query
        return execute_query("SELECT * FROM temu_price_adjustments WHERE user_id=? AND shop_id=? ORDER BY created_at DESC LIMIT ?",(self.user_id,shop_id,limit),fetch=True) or []

import logging; from typing import List; from modules.dashboard.schemas import ServiceResult, DashboardOverview; logger=logging.getLogger(__name__)

class DashboardService:
    def __init__(self, user_id: int): self.user_id = user_id

    async def get_overview(self) -> ServiceResult:
        logger.info(f"获取总控大屏数据 | user_id={self.user_id}")
        shops = self._get_user_shops()
        total_profit=0.0; total_revenue=0.0; pricing_pending=0; inventory_alerts=0; risk_warnings=0; review_alerts=0
        shop_cards=[]
        for shop in shops:
            sid=shop["shop_id"]; sname=shop["shop_name"]
            p=self._get_shop_profit(sid); r=self._get_shop_revenue(sid)
            total_profit+=p; total_revenue+=r
            pp=self._get_pricing_pending(sid); ia=self._get_inventory_alert_count(sid)
            rw=self._get_risk_warning_count(sid); ra=self._get_review_alert_count(sid)
            pricing_pending+=pp; inventory_alerts+=ia; risk_warnings+=rw; review_alerts+=ra
            shop_cards.append({"shop_id":sid,"shop_name":sname,"profit":round(p,2),"revenue":round(r,2), "pricing_pending":pp,"inventory_alerts":ia,"risk_warnings":rw,"review_alerts":ra})
        overview = DashboardOverview(total_profit=round(total_profit,2),total_revenue=round(total_revenue,2),
            total_alerts=pricing_pending+inventory_alerts+risk_warnings+review_alerts,
            pricing_pending=pricing_pending, inventory_alerts=inventory_alerts, risk_warnings=risk_warnings,
            review_alerts=review_alerts, shop_count=len(shops), shop_details=shop_cards)
        return ServiceResult(success=True,data={"overview":overview.__dict__})

    async def get_all_alerts(self) -> ServiceResult:
        shops=self._get_user_shops(); alerts=[]
        for shop in shops:
            sid=shop["shop_id"]; sname=shop["shop_name"]
            for a in self._get_pricing_expiring(sid): alerts.append({"shop":sname,"shop_id":sid,"type":"核价超时","msg":a,"severity":"high"})
            for a in self._get_inventory_alerts(sid): alerts.append({"shop":sname,"shop_id":sid,"type":a.get("type","库存"),"msg":a.get("message",""),"severity":"medium"})
            for a in self._get_review_alerts(sid): alerts.append({"shop":sname,"shop_id":sid,"type":"差评","msg":a,"severity":"medium"})
        alerts.sort(key=lambda x:{"high":0,"medium":1,"low":2}.get(x["severity"],3))
        return ServiceResult(success=True,data={"alerts":alerts,"count":len(alerts)})

    def _get_user_shops(self) -> list:
        from db import execute_query
        return execute_query("SELECT shop_id,shop_name FROM temu_shops WHERE user_id=?",(self.user_id,),fetch=True) or []
    def _get_shop_profit(self, shop_id: int) -> float:
        from db import execute_query
        rows=execute_query("SELECT SUM(total_profit) as p FROM temu_profit_stats WHERE user_id=? AND shop_id=?",(self.user_id,shop_id),fetch=True)
        return float(rows[0]["p"]) if rows and rows[0]["p"] else 0.0
    def _get_shop_revenue(self, shop_id: int) -> float:
        from db import execute_query
        rows=execute_query("SELECT SUM(total_revenue) as r FROM temu_profit_stats WHERE user_id=? AND shop_id=?",(self.user_id,shop_id),fetch=True)
        return float(rows[0]["r"]) if rows and rows[0]["r"] else 0.0
    def _get_pricing_pending(self, shop_id: int) -> int:
        from db import execute_query
        rows=execute_query("SELECT COUNT(*) as c FROM temu_pricing_logs WHERE user_id=? AND shop_id=? AND action='skip'",(self.user_id,shop_id),fetch=True)
        return rows[0]["c"] if rows else 0
    def _get_inventory_alert_count(self, shop_id: int) -> int:
        from db import execute_query
        rows=execute_query("SELECT COUNT(*) as c FROM temu_inventory_alerts WHERE user_id=? AND shop_id=? AND is_read=0",(self.user_id,shop_id),fetch=True)
        return rows[0]["c"] if rows else 0
    def _get_risk_warning_count(self, shop_id: int) -> int:
        from db import execute_query
        rows=execute_query("SELECT COUNT(*) as c FROM temu_risk_metrics WHERE user_id=? AND shop_id=? AND comprehensive_score<80",(self.user_id,shop_id),fetch=True)
        return rows[0]["c"] if rows else 0
    def _get_review_alert_count(self, shop_id: int) -> int:
        return 0
    def _get_pricing_expiring(self, shop_id: int) -> list:
        return []
    def _get_inventory_alerts(self, shop_id: int) -> list:
        from db import execute_query
        return execute_query("SELECT alert_type,message FROM temu_inventory_alerts WHERE user_id=? AND shop_id=? AND is_read=0",(self.user_id,shop_id),fetch=True) or []
    def _get_review_alerts(self, shop_id: int) -> list:
        return []

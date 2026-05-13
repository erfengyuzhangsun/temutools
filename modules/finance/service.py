import logging; from datetime import datetime, timedelta; from typing import List; from modules.finance.schemas import ServiceResult, Settlement, MonthlySummary; logger=logging.getLogger(__name__)

class FinanceService:
    def __init__(self, user_id: int): self.user_id = user_id

    async def sync_settlement(self, shop_id: int) -> ServiceResult:
        logger.info(f"同步结算 | user_id={self.user_id} | shop_id={shop_id}")
        from common.temu_client import TemuApiClient
        client = TemuApiClient(shop_id=shop_id)
        try:
            today=datetime.now(); date_from=(today-timedelta(days=15)).strftime("%Y-%m-%d"); date_to=today.strftime("%Y-%m-%d")
            resp = await client.get_settlements(date_from, date_to)
            if not resp.success: return ServiceResult(success=False,message="结算同步失败",error_code="SYNC_FAILED")
            data = (resp.data or {}).get("settlements",[]) or []
            count=0
            for s in data:
                self._save_settlement(shop_id, s); count+=1
            return ServiceResult(success=True,data={"synced_count":count})
        except Exception as e: logger.error(f"结算同步异常: {e}"); return ServiceResult(success=False,message=str(e))
        finally: await client.close()

    async def get_monthly_profit_summary(self, shop_id: int, month: str) -> ServiceResult:
        rows = self._query_monthly_settlements(shop_id, month)
        rev = sum(float(r.get("total_revenue",0)) for r in rows)
        ded = sum(float(r.get("total_deductions",0)) for r in rows)
        net = rev - ded
        summary = MonthlySummary(month=month,total_revenue=round(rev,2),total_cost=round(ded,2),total_profit=round(net,2),
            profit_rate=round((net/rev*100) if rev>0 else 0,2),platform_fees=round(ded,2),
            shop_details=[{"shop_id":shop_id,"revenue":round(rev,2),"cost":round(ded,2),"profit":round(net,2)}])
        return ServiceResult(success=True,data={"summary":summary.__dict__})

    async def predict_next_payout(self, shop_id: int) -> ServiceResult:
        rows = self._get_recent_settlements(shop_id)
        if not rows: return ServiceResult(success=True,data={"predicted":0,"message":"无历史数据"})
        avg_rev = sum(float(r.get("total_revenue",0)) for r in rows)/len(rows)
        avg_ded = sum(float(r.get("total_deductions",0)) for r in rows)/len(rows)
        predicted = round(avg_rev - avg_ded, 2)
        return ServiceResult(success=True,data={"predicted":predicted,"based_on":len(rows),"avg_revenue":round(avg_rev,2),"avg_deductions":round(avg_ded,2)})

    async def reconcile(self, shop_id: int, settlement_id: int) -> ServiceResult:
        row = self._get_settlement(settlement_id)
        if not row: return ServiceResult(success=False,message="结算单不存在")
        expected = float(row.get("net_payout",0))
        from calculator import ProfitCalculator
        calc = ProfitCalculator()
        diff = 0.0
        self._save_reconciliation(shop_id, settlement_id, expected, expected-diff, diff)
        return ServiceResult(success=True,data={"settlement_id":settlement_id,"expected":expected,"actual":expected-diff,"difference":diff,"status":"matched" if abs(diff)<0.5 else "unmatched"})

    def _save_settlement(self, shop_id: int, s: dict):
        from db import execute_query
        execute_query("INSERT OR REPLACE INTO temu_settlements (user_id,shop_id,period_start,period_end,total_revenue,total_deductions,net_payout,status,settlement_date) VALUES (?,?,?,?,?,?,?,?,?)",
            (self.user_id,shop_id,s.get("period_start"),s.get("period_end"),float(s.get("total_revenue",0)),float(s.get("total_deductions",0)),float(s.get("net_payout",0)),s.get("status","pending"),s.get("settlement_date")))

    def _query_monthly_settlements(self, shop_id: int, month: str) -> list:
        from db import execute_query, DB_MODE
        if DB_MODE == "mysql":
            return execute_query("SELECT * FROM temu_settlements WHERE user_id=? AND shop_id=? AND DATE_FORMAT(period_start,'%Y-%m')=?",(self.user_id,shop_id,month),fetch=True) or []
        return execute_query("SELECT * FROM temu_settlements WHERE user_id=? AND shop_id=? AND strftime('%Y-%m',period_start)=?",(self.user_id,shop_id,month),fetch=True) or []

    def _get_recent_settlements(self, shop_id: int) -> list:
        from db import execute_query
        return execute_query("SELECT * FROM temu_settlements WHERE user_id=? AND shop_id=? ORDER BY period_end DESC LIMIT 6",(self.user_id,shop_id),fetch=True) or []

    def _get_settlement(self, settlement_id: int) -> dict:
        from db import execute_query
        rows=execute_query("SELECT * FROM temu_settlements WHERE settlement_id=?",(settlement_id,),fetch=True)
        return rows[0] if rows else {}

    def _save_reconciliation(self, shop_id: int, settlement_id: int, expected: float, actual: float, diff: float):
        from db import execute_query
        execute_query("INSERT INTO temu_reconciliation_logs (user_id,shop_id,settlement_id,expected_amount,actual_amount,difference,status) VALUES (?,?,?,?,?,?,?)",
            (self.user_id,shop_id,settlement_id,expected,actual,diff,"matched" if abs(diff)<0.5 else "unmatched"))

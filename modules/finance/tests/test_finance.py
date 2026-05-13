import pytest
pytestmark = pytest.mark.asyncio
class TestFinanceNormal:
    async def test_sync_settlement(self, mock_temu_client):
        from modules.finance.service import FinanceService; from common.temu_client import TemuApiResponse
        s=FinanceService(1)
        mock_temu_client.get_settlements.return_value=TemuApiResponse(True,{"settlements":[{"period_start":"2026-05-01","period_end":"2026-05-15","total_revenue":50000,"total_deductions":3000,"net_payout":47000,"status":"completed"}]})
        r=await s.sync_settlement(1)
        assert r.success; assert r.data["synced_count"]==1

    async def test_monthly_profit_summary(self, mock_temu_client):
        from modules.finance.service import FinanceService
        s=FinanceService(1)
        s._query_monthly_settlements=lambda sid,m:[{"total_revenue":100000,"total_deductions":20000},{"total_revenue":80000,"total_deductions":15000}]
        r=await s.get_monthly_profit_summary(1,"2026-05")
        assert r.success; assert r.data["summary"]["total_revenue"]==180000; assert r.data["summary"]["total_profit"]==145000

    async def test_predict_next_payout(self, mock_temu_client):
        from modules.finance.service import FinanceService
        s=FinanceService(1)
        s._get_recent_settlements=lambda sid:[{"total_revenue":50000,"total_deductions":3000}]*3
        r=await s.predict_next_payout(1)
        assert r.success; assert r.data["predicted"]==47000.0

    async def test_reconcile(self, mock_temu_client):
        from modules.finance.service import FinanceService
        s=FinanceService(1)
        s._get_settlement=lambda sid:{"net_payout":47000.0}
        r=await s.reconcile(1,1)
        assert r.success; assert r.data["status"]=="matched"

    async def test_empty_settlement(self, mock_temu_client):
        from modules.finance.service import FinanceService
        s=FinanceService(1)
        s._get_recent_settlements=lambda sid:[]
        r=await s.predict_next_payout(1)
        assert r.success; assert r.data["predicted"]==0

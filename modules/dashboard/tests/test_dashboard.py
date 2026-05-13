import pytest; from unittest.mock import AsyncMock
pytestmark = pytest.mark.asyncio

class TestDashboardNormal:
    async def test_overview_aggregation(self):
        from modules.dashboard.service import DashboardService
        s=DashboardService(1)
        s._get_user_shops=lambda:[{"shop_id":1,"shop_name":"店铺A"},{"shop_id":2,"shop_name":"店铺B"}]
        s._get_shop_profit=lambda sid:40000 if sid==1 else 30000
        s._get_shop_revenue=lambda sid:100000 if sid==1 else 80000
        s._get_pricing_pending=lambda sid:2
        s._get_inventory_alert_count=lambda sid:1
        s._get_risk_warning_count=lambda sid:0
        s._get_review_alert_count=lambda sid:0
        r=await s.get_overview()
        assert r.success; assert r.data["overview"]["total_profit"]==70000.0
        assert r.data["overview"]["total_revenue"]==180000.0
        assert r.data["overview"]["shop_count"]==2

    async def test_all_alerts_aggregation(self):
        from modules.dashboard.service import DashboardService
        s=DashboardService(1)
        s._get_user_shops=lambda:[{"shop_id":1,"shop_name":"店铺A"}]
        s._get_pricing_expiring=lambda sid:["核价PRC001即将超时"]
        s._get_inventory_alerts=lambda sid:[{"type":"low_stock","message":"SKU001库存不足"}]
        s._get_review_alerts=lambda sid:["新差评SKU002"]
        r=await s.get_all_alerts()
        assert r.success; assert r.data["count"]==3

    async def test_no_shops(self):
        from modules.dashboard.service import DashboardService
        s=DashboardService(1)
        s._get_user_shops=lambda:[]
        r=await s.get_overview()
        assert r.success; assert r.data["overview"]["shop_count"]==0; assert r.data["overview"]["total_alerts"]==0

    async def test_config(self):
        from modules.dashboard.config import MODULE_CONFIG
        assert "auto_refresh_interval" in MODULE_CONFIG

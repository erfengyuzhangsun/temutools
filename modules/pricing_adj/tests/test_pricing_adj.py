import pytest
pytestmark = pytest.mark.asyncio

class TestPriceAdjNormal:
    async def test_auto_adjust_competitor_drop(self, mock_temu_client):
        from modules.pricing_adj.service import PricingAdjustmentService
        s=PricingAdjustmentService(1)
        s._get_current_price=lambda sid,sku:120.0
        s._get_cost_price=lambda sid,sku:80.0
        s._get_competitor_price=lambda sku:100.0
        s._get_today_adjustment_count=lambda sid:0
        r=await s.auto_adjust_price(1,"SKU001")
        assert r.success; assert r.data["new_price"]<120.0

    async def test_auto_adjust_no_competitor(self, mock_temu_client):
        from modules.pricing_adj.service import PricingAdjustmentService
        s=PricingAdjustmentService(1)
        s._get_current_price=lambda sid,sku:120.0
        s._get_cost_price=lambda sid,sku:80.0
        s._get_competitor_price=lambda sku:0.0
        s._get_today_adjustment_count=lambda sid:0
        r=await s.auto_adjust_price(1,"SKU001")
        assert r.success; assert r.data["new_price"]==120.0

    async def test_rate_limit_exceeded(self, mock_temu_client):
        from modules.pricing_adj.service import PricingAdjustmentService
        s=PricingAdjustmentService(1)
        s._get_today_adjustment_count=lambda sid:10
        r=await s.auto_adjust_price(1,"SKU001")
        assert not r.success; assert r.error_code=="RATE_LIMIT"

    async def test_activity_price_switch(self, mock_temu_client):
        from modules.pricing_adj.service import PricingAdjustmentService
        s=PricingAdjustmentService(1)
        s._get_current_price=lambda sid,sku:150.0
        r=await s.adjust_for_activity(1,"SKU001",120.0)
        assert r.success; assert r.data["new_price"]==120.0

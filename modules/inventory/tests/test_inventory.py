import pytest; from unittest.mock import AsyncMock
pytestmark = pytest.mark.asyncio

class TestInvNormal:
    async def test_sync_inventory(self, mock_temu_client):
        from modules.inventory.service import InventoryService
        from common.temu_client import TemuApiResponse
        s=InventoryService(1)
        mock_temu_client.get_inventory.return_value=TemuApiResponse(True,{"inventory":[{"sku":"A","current_stock":100},{"sku":"B","current_stock":50,"safety_stock":20},{"sku":"C","current_stock":0}]})
        r=await s.sync_inventory(1)
        assert r.success; assert r.data["synced_count"]==3

    async def test_low_stock_alert(self, mock_temu_client):
        from modules.inventory.service import InventoryService
        s=InventoryService(1)
        s._get_all_inventory=lambda sid:[{"sku":"A","current_stock":15,"safety_stock":20,"product_name":"P","daily_avg_sales":5,"lead_time_days":3,"cost_price":50},{"sku":"B","current_stock":0,"safety_stock":10,"product_name":"Q","daily_avg_sales":0,"lead_time_days":3,"cost_price":30}]
        r=await s.check_inventory_alerts(1)
        assert r.success; assert r.data["alert_count"]>=2

    async def test_replenishment(self, mock_temu_client):
        from modules.inventory.service import InventoryService
        s=InventoryService(1)
        s._get_all_inventory=lambda sid:[{"sku":"A","current_stock":30,"safety_stock":20,"daily_avg_sales":10,"lead_time_days":7,"cost_price":50,"product_name":"P"}]
        r=await s.generate_replenishment_suggestions(1)
        assert r.success; assert r.data["count"]==1
        sug=r.data["suggestions"][0]
        assert sug["sku"]=="A"; assert sug["suggested_quantity"]==60

    async def test_empty_inventory(self, mock_temu_client):
        from modules.inventory.service import InventoryService
        s=InventoryService(1); s._get_all_inventory=lambda sid:[]
        r=await s.generate_replenishment_suggestions(1)
        assert r.success; assert r.data["count"]==0

class TestInvConfig:
    def test_config(self):
        from modules.inventory.config import MODULE_CONFIG
        for k in ["safety_stock_days","slow_moving_days","replenishment_lead_time_default"]:
            assert k in MODULE_CONFIG

import os,sys
import tempfile
_db=tempfile.NamedTemporaryFile(suffix=".db",delete=False);_dp=_db.name;_db.close()
os.environ["DB_MODE"]="sqlite";os.environ["SQLITE_PATH"]=_dp
from cryptography.fernet import Fernet;os.environ["ENCRYPTION_KEY"]=Fernet.generate_key().decode()
os.environ["SEED_ADMIN_PASSWORD"]="test-seed-pwd"

from db import initialize_database;initialize_database()
from modules.inventory.models import initialize_tables as m4;m4()
from modules.analysis.models import initialize_tables as m5;m5()
from modules.pricing_adj.models import initialize_tables as m6;m6()
from modules.finance.models import initialize_tables as m7;m7()

from unittest.mock import AsyncMock, patch
import pytest;pytestmark=pytest.mark.asyncio

# ============ Module 4: Inventory ============
class TestInventory:
    @patch("common.temu_client.TemuApiClient")
    async def test_sync(self,mc):
        from modules.inventory.service import InventoryService as S;from common.temu_client import TemuApiResponse
        m=AsyncMock();mc.return_value=m;m.get_inventory.return_value=TemuApiResponse(True,{"inventory":[{"sku":"A","current_stock":100},{"sku":"B","current_stock":50}]})
        r=await S(1).sync_inventory(1);assert r.success;assert r.data["synced_count"]==2
    async def test_alerts(self):
        from modules.inventory.service import InventoryService as S
        s=S(1);s._get_all_inventory=lambda sid:[{"sku":"A","current_stock":5,"safety_stock":20,"product_name":"P","daily_avg_sales":3,"lead_time_days":7,"cost_price":50}]
        r=await s.check_inventory_alerts(1);assert r.success;assert r.data["alert_count"]>=1
    async def test_replenish(self):
        from modules.inventory.service import InventoryService as S
        s=S(1);s._get_all_inventory=lambda sid:[{"sku":"A","current_stock":30,"safety_stock":20,"daily_avg_sales":10,"lead_time_days":7,"cost_price":50,"product_name":"P"}]
        r=await s.generate_replenishment_suggestions(1);assert r.success;assert r.data["count"]==1;assert r.data["suggestions"][0]["suggested_quantity"]==60
    async def test_empty_inv(self):
        from modules.inventory.service import InventoryService as S
        s=S(1);s._get_all_inventory=lambda sid:[];r=await s.generate_replenishment_suggestions(1);assert r.success;assert r.data["count"]==0

# ============ Module 5: Analysis ============
class TestAnalysis:
    @patch("common.temu_client.TemuApiClient")
    async def test_collect(self,mc):
        from modules.analysis.service import AnalysisService as S;from common.temu_client import TemuApiResponse
        m=AsyncMock();mc.return_value=m
        m.get_shop_metrics.return_value=TemuApiResponse(True,{"metrics":{"impressions":5000,"clicks":200,"click_rate":4.0,"conversion_rate":4.0,"return_rate":8.0,"total_sales":50000,"total_orders":50}})
        r=await S(1).collect_metrics(1);assert r.success;assert r.data["metrics"]["impressions"]==5000
    async def test_alert_conv(self):
        from modules.analysis.service import AnalysisService as S
        s=S(1);s._get_latest_metrics=lambda sid:[{"conversion_rate":2.0,"return_rate":18.0,"impressions":1000,"clicks":20,"total_sales":1000,"total_orders":10}]
        r=await s.check_metric_alerts(1);assert r.success;assert r.data["alert_count"]>=2
    async def test_report(self):
        from modules.analysis.service import AnalysisService as S
        s=S(1);s._get_metrics_range=lambda sid,days:[{"impressions":1000,"conversion_rate":3.5,"return_rate":8.0,"date":"2026-05-13","total_sales":10000,"total_orders":50}]
        r=await s.generate_report(1,"weekly");assert r.success;assert r.data["report"]["report_type"]=="weekly"

# ============ Module 6: Pricing Adj ============
class TestPricingAdj:
    async def test_auto_adj(self):
        from modules.pricing_adj.service import PricingAdjustmentService as S
        s=S(1);s._get_current_price=lambda sid,sku:120.0;s._get_cost_price=lambda sid,sku:80.0
        s._get_competitor_price=lambda sku:100.0;s._get_today_adjustment_count=lambda sid:0
        r=await s.auto_adjust_price(1,"SKU001");assert r.success;assert r.data["new_price"]<120.0 or abs(r.data["new_price"]-125.0)<0.01
    async def test_ratelimit(self):
        from modules.pricing_adj.service import PricingAdjustmentService as S
        s=S(1);s._get_today_adjustment_count=lambda sid:10
        r=await s.auto_adjust_price(1,"SKU001");assert not r.success
    async def test_activity(self):
        from modules.pricing_adj.service import PricingAdjustmentService as S
        s=S(1);s._get_current_price=lambda sid,sku:150.0
        r=await s.adjust_for_activity(1,"SKU001",120.0);assert r.success;assert r.data["new_price"]==120.0

# ============ Module 7: Finance ============
class TestFinance:
    @patch("common.temu_client.TemuApiClient")
    async def test_sync(self,mc):
        from modules.finance.service import FinanceService as S;from common.temu_client import TemuApiResponse
        m=AsyncMock();mc.return_value=m
        m.get_settlements.return_value=TemuApiResponse(True,{"settlements":[{"period_start":"2026-05-01","period_end":"2026-05-15","total_revenue":50000,"total_deductions":3000,"net_payout":47000,"status":"completed"}]})
        r=await S(1).sync_settlement(1);assert r.success;assert r.data["synced_count"]==1
    async def test_monthly(self):
        from modules.finance.service import FinanceService as S
        s=S(1);s._query_monthly_settlements=lambda sid,m:[{"total_revenue":100000,"total_deductions":20000}]
        r=await s.get_monthly_profit_summary(1,"2026-05");assert r.success;assert r.data["summary"]["total_revenue"]==100000;assert r.data["summary"]["total_profit"]==80000
    async def test_predict(self):
        from modules.finance.service import FinanceService as S
        s=S(1);s._get_recent_settlements=lambda sid:[{"total_revenue":50000,"total_deductions":3000}]*3
        r=await s.predict_next_payout(1);assert r.success;assert r.data["predicted"]==47000.0
    async def test_reconcile(self):
        from modules.finance.service import FinanceService as S
        s=S(1);s._get_settlement=lambda sid:{"net_payout":47000.0};r=await s.reconcile(1,1);assert r.success;assert r.data["status"]=="matched"

# ============ Module 8: Dashboard ============
class TestDashboard:
    async def test_overview(self):
        from modules.dashboard.service import DashboardService as S
        s=S(1);s._get_user_shops=lambda:[{"shop_id":1,"shop_name":"A"}]
        s._get_shop_profit=lambda sid:40000;s._get_shop_revenue=lambda sid:100000
        s._get_pricing_pending=lambda sid:2;s._get_inventory_alert_count=lambda sid:1
        s._get_risk_warning_count=lambda sid:0;s._get_review_alert_count=lambda sid:0
        r=await s.get_overview();assert r.success;assert r.data["overview"]["total_profit"]==40000.0;assert r.data["overview"]["shop_count"]==1
    async def test_alerts(self):
        from modules.dashboard.service import DashboardService as S
        s=S(1);s._get_user_shops=lambda:[{"shop_id":1,"shop_name":"A"}]
        s._get_pricing_expiring=lambda sid:["核价超时"];s._get_inventory_alerts=lambda sid:[{"type":"low_stock","message":"库存不足"}]
        s._get_review_alerts=lambda sid:["差评"]
        r=await s.get_all_alerts();assert r.success;assert r.data["count"]==3
    async def test_no_shops(self):
        from modules.dashboard.service import DashboardService as S
        s=S(1);s._get_user_shops=lambda:[];r=await s.get_overview();assert r.success;assert r.data["overview"]["shop_count"]==0

# ============ Config ============
class TestConfig:
    def test_inv(self):from modules.inventory.config import MODULE_CONFIG;assert "safety_stock_days" in MODULE_CONFIG
    def test_ana(self):from modules.analysis.config import MODULE_CONFIG;assert "conversion_rate_alert_threshold" in MODULE_CONFIG
    def test_padj(self):from modules.pricing_adj.config import MODULE_CONFIG;assert "min_gross_margin" in MODULE_CONFIG
    def test_fin(self):from modules.finance.config import MODULE_CONFIG;assert "auto_sync_settlement" in MODULE_CONFIG
    def test_dash(self):from modules.dashboard.config import MODULE_CONFIG;assert "auto_refresh_interval" in MODULE_CONFIG

def teardown_module(module):
    try:os.unlink(_dp)
    except:pass

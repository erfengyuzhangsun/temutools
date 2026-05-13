import pytest; from unittest.mock import AsyncMock
pytestmark = pytest.mark.asyncio

class TestAnalysisNormal:
    async def test_collect_metrics(self, mock_temu_client):
        from modules.analysis.service import AnalysisService; from common.temu_client import TemuApiResponse
        s=AnalysisService(1)
        mock_temu_client.get_shop_metrics.return_value=TemuApiResponse(True,{"metrics":{"impressions":5000,"clicks":200,"click_rate":4.0,"conversion_rate":4.0,"return_rate":8.0,"total_sales":50000,"total_orders":50}})
        r=await s.collect_metrics(1)
        assert r.success; assert r.data["metrics"]["impressions"]==5000; assert r.data["metrics"]["click_rate"]==4.0

    async def test_alert_on_low_conversion(self, mock_temu_client):
        from modules.analysis.service import AnalysisService
        s=AnalysisService(1)
        s._get_latest_metrics=lambda sid:[{"conversion_rate":2.0,"return_rate":8.0,"impressions":1000,"clicks":20,"total_sales":1000,"total_orders":10}]
        r=await s.check_metric_alerts(1)
        assert r.success; assert r.data["alert_count"]>=1
        assert any(a["type"]=="conversion_rate" for a in r.data["alerts"])

    async def test_alert_on_high_return_rate(self, mock_temu_client):
        from modules.analysis.service import AnalysisService
        s=AnalysisService(1)
        s._get_latest_metrics=lambda sid:[{"conversion_rate":5.0,"return_rate":18.0,"impressions":1000,"clicks":50,"total_sales":1000,"total_orders":20}]
        r=await s.check_metric_alerts(1)
        assert r.success; assert r.data["alert_count"]>=1
        assert any(a["type"]=="return_rate" for a in r.data["alerts"])

    async def test_generate_weekly_report(self, mock_temu_client):
        from modules.analysis.service import AnalysisService
        s=AnalysisService(1)
        s._get_metrics_range=lambda sid,days:[{"impressions":1000,"conversion_rate":3.5,"return_rate":8.0,"date":"2026-05-13","total_sales":10000,"total_orders":50}]
        r=await s.generate_report(1,"weekly")
        assert r.success; assert r.data["report"]["report_type"]=="weekly"

class TestAnalysisConfig:
    def test_config(self):
        from modules.analysis.config import MODULE_CONFIG
        for k in["conversion_rate_alert_threshold","return_rate_alert_threshold"]: assert k in MODULE_CONFIG

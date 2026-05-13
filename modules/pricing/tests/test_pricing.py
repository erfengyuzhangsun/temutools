"""模块2：核价自动化 - 全覆盖测试

RED阶段：测试先行，业务代码尚未实现
遵循AAA模式：Arrange → Act → Assert
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
class TestPricingNormalFlow:
    """正常流程测试"""

    async def test_auto_accept_pricing_above_threshold(self, mock_temu_client):
        from modules.pricing.service import PricingService

        service = PricingService(user_id=1)
        profit_threshold = 20.0
        service._get_profit_threshold = AsyncMock(return_value=profit_threshold)
        service._get_cost_price = AsyncMock(return_value=80.0)

        notice = {
            "notice_id": "PRC001",
            "sku": "SKU001",
            "supply_price": 100.0,
            "is_activity": False,
        }
        mock_temu_client.get_pricing_notices.return_value = type("Resp", (), {
            "success": True, "data": {"notices": [notice], "total": 1}
        })()

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.success is True
        assert result.data["handled_count"] == 1
        assert result.data["results"][0]["action"] == "accept"
        assert result.data["results"][0]["gross_margin"] == 25.0

    async def test_auto_reject_pricing_below_threshold(self, mock_temu_client):
        from modules.pricing.service import PricingService

        service = PricingService(user_id=1)
        profit_threshold = 20.0
        service._get_profit_threshold = AsyncMock(return_value=profit_threshold)
        service._get_cost_price = AsyncMock(return_value=80.0)

        notice = {
            "notice_id": "PRC002",
            "sku": "SKU002",
            "supply_price": 90.0,
            "is_activity": False,
        }
        mock_temu_client.get_pricing_notices.return_value = type("Resp", (), {
            "success": True, "data": {"notices": [notice], "total": 1}
        })()

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.success is True
        assert result.data["handled_count"] == 1
        assert result.data["results"][0]["action"] == "reject"
        assert result.data["results"][0]["gross_margin"] == 12.5

    async def test_activity_item_uses_activity_threshold(self, mock_temu_client):
        from modules.pricing.service import PricingService

        service = PricingService(user_id=1)
        service._get_profit_threshold = AsyncMock(return_value=20.0)
        service._get_activity_profit_threshold = AsyncMock(return_value=10.0)
        service._get_cost_price = AsyncMock(return_value=80.0)

        notice = {
            "notice_id": "PRC003",
            "sku": "SKU003",
            "supply_price": 88.0,
            "is_activity": True,
        }
        mock_temu_client.get_pricing_notices.return_value = type("Resp", (), {
            "success": True, "data": {"notices": [notice], "total": 1}
        })()

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.success is True
        assert result.data["results"][0]["action"] == "accept"
        assert result.data["results"][0]["gross_margin"] == 10.0

    async def test_pricing_expiry_reminder(self, mock_temu_client):
        from modules.pricing.service import PricingService

        service = PricingService(user_id=1)
        soon = (datetime.now() + timedelta(hours=1)).isoformat()
        notice = {
            "notice_id": "PRC004",
            "sku": "SKU004",
            "supply_price": 100.0,
            "is_activity": False,
            "expire_at": soon,
        }
        mock_temu_client.get_pricing_notices.return_value = type("Resp", (), {
            "success": True, "data": {"notices": [notice], "total": 1}
        })()
        service._get_cost_price = AsyncMock(return_value=80.0)
        service._get_profit_threshold = AsyncMock(return_value=20.0)
        mock_temu_client.accept_pricing = AsyncMock(return_value=type("Resp", (), {"success": True})())

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.success is True
        expiring = result.data.get("expiring_soon", [])
        assert len(expiring) == 1
        assert expiring[0]["notice_id"] == "PRC004"

    async def test_pricing_log_query(self, mock_temu_client):
        from modules.pricing.service import PricingService
        from modules.pricing.schemas import PricingLogItem

        service = PricingService(user_id=1)
        mock_logs = [
            PricingLogItem(log_id=1, notice_id="PRC001", sku="SKU001",
                           action="accept", supply_price=100.0, cost_price=80.0,
                           gross_margin=25.0, handled_at=datetime.now()),
            PricingLogItem(log_id=2, notice_id="PRC002", sku="SKU002",
                           action="reject", supply_price=90.0, cost_price=80.0,
                           gross_margin=12.5, handled_at=datetime.now()),
        ]
        service._get_pricing_logs_from_db = AsyncMock(return_value=mock_logs)

        logs = await service.get_pricing_logs(shop_id=1)

        assert len(logs) == 2
        assert logs[0].action == "accept"
        assert logs[1].action == "reject"


@pytest.mark.asyncio
class TestPricingExceptionFlow:
    """异常场景测试"""

    async def test_pricing_data_missing_cost_price(self, mock_temu_client):
        from modules.pricing.service import PricingService

        service = PricingService(user_id=1)
        service._get_cost_price = AsyncMock(return_value=None)

        notice = {
            "notice_id": "PRC005",
            "sku": "SKU005",
            "supply_price": 100.0,
            "is_activity": False,
        }
        mock_temu_client.get_pricing_notices.return_value = type("Resp", (), {
            "success": True, "data": {"notices": [notice], "total": 1}
        })()

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.success is True
        assert result.data["results"][0]["action"] == "skip"
        assert "待人工处理" in result.data["results"][0]["reason"]

    async def test_api_failure_during_pricing_sync(self, mock_temu_client):
        from modules.pricing.service import PricingService
        from common.temu_client import TemuApiServerError

        service = PricingService(user_id=1)
        mock_temu_client.get_pricing_notices.side_effect = TemuApiServerError(
            "服务器错误", status_code=503
        )

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.success is False
        assert result.error_code == "SERVER_ERROR"

    async def test_multi_sku_mixed_results(self, mock_temu_client):
        from modules.pricing.service import PricingService

        service = PricingService(user_id=1)
        service._get_profit_threshold = AsyncMock(return_value=20.0)
        service._get_cost_price = AsyncMock(side_effect=[80.0, 80.0, 50.0, None])

        notices = [
            {"notice_id": "PRC006", "sku": "SKU006", "supply_price": 100.0, "is_activity": False},
            {"notice_id": "PRC007", "sku": "SKU007", "supply_price": 90.0, "is_activity": False},
            {"notice_id": "PRC008", "sku": "SKU008", "supply_price": 60.0, "is_activity": False},
            {"notice_id": "PRC009", "sku": "SKU009", "supply_price": 120.0, "is_activity": False},
        ]
        mock_temu_client.get_pricing_notices.return_value = type("Resp", (), {
            "success": True, "data": {"notices": notices, "total": 4}
        })()

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.data["handled_count"] == 4
        results = result.data["results"]
        assert results[0]["action"] == "accept"
        assert results[1]["action"] == "reject"
        assert results[2]["action"] == "accept"
        assert results[3]["action"] == "skip"


@pytest.mark.asyncio
class TestPricingBoundaryValue:
    """边界值测试"""

    async def test_exact_threshold_boundary_accept(self, mock_temu_client):
        from modules.pricing.service import PricingService

        service = PricingService(user_id=1)
        service._get_profit_threshold = AsyncMock(return_value=20.0)
        service._get_cost_price = AsyncMock(return_value=80.0)

        notice = {
            "notice_id": "PRC010",
            "sku": "SKU010",
            "supply_price": 96.0,
            "is_activity": False,
        }
        mock_temu_client.get_pricing_notices.return_value = type("Resp", (), {
            "success": True, "data": {"notices": [notice], "total": 1}
        })()

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.data["results"][0]["action"] == "accept"
        assert result.data["results"][0]["gross_margin"] == 20.0

    async def test_empty_pricing_notices(self, mock_temu_client):
        from modules.pricing.service import PricingService

        service = PricingService(user_id=1)
        mock_temu_client.get_pricing_notices.return_value = type("Resp", (), {
            "success": True, "data": {"notices": [], "total": 0}
        })()

        result = await service.auto_handle_pricing(shop_id=1)

        assert result.success is True
        assert result.data["handled_count"] == 0


class TestPricingConfig:
    """配置测试"""

    def test_config_has_required_keys(self):
        from modules.pricing.config import MODULE_CONFIG

        required_keys = ["default_profit_threshold", "activity_profit_threshold",
                         "expiry_reminder_hours", "max_notices_per_page"]
        for key in required_keys:
            assert key in MODULE_CONFIG, f"缺少配置项: {key}"

    def test_config_values_are_valid(self):
        from modules.pricing.config import MODULE_CONFIG

        threshold = MODULE_CONFIG["default_profit_threshold"]
        assert 0 <= threshold["min"] <= threshold["default"] <= threshold["max"]

        activity = MODULE_CONFIG["activity_profit_threshold"]
        assert activity["default"] <= threshold["default"]

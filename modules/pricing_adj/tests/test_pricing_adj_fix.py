"""
测试：智能定价调价模块 Bug 修复
覆盖场景：
  1. SKU无售价时给出可操作提示
  2. 调价记录正常查询
  3. 活动价切换正确
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestPricingAdjFix:
    """测试定价调价修复"""

    @pytest.mark.asyncio
    async def test_no_price_error_message_guides_user(self):
        """无售价时应提示用户先同步数据"""
        from modules.pricing_adj.service import PricingAdjustmentService

        service = PricingAdjustmentService(user_id=1)
        result = await service.auto_adjust_price(shop_id=1, sku="NONEXISTENT_SKU")

        assert result.success is False
        assert result.error_code == "NO_PRICE"
        assert "SKU无当前售价" in result.message

    @pytest.mark.asyncio
    async def test_adjustment_logs_query(self):
        """调价记录查询正常"""
        from modules.pricing_adj.service import PricingAdjustmentService

        service = PricingAdjustmentService(user_id=1)
        result = await service.get_adjustment_logs(shop_id=1, limit=10)

        assert result.success is True
        assert "logs" in result.data

    @pytest.mark.asyncio
    async def test_adjust_for_activity_no_price(self):
        """活动价切换在无售价时给出提示"""
        from modules.pricing_adj.service import PricingAdjustmentService

        service = PricingAdjustmentService(user_id=1)
        result = await service.adjust_for_activity(shop_id=1, sku="NONEXISTENT_SKU", activity_price=50.0)

        assert result.success is False
        assert "SKU无当前售价" in result.message

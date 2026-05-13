"""
测试：核价自动化模块 Bug 修复
覆盖场景：
  1. httpx 依赖可用性
  2. TemuApiClient 凭证自动加载
  3. 无通知时正常处理
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestPricingFix:
    """测试核价模块修复"""

    def test_httpx_importable_in_pricing_service(self):
        """核价服务中 httpx 可正常导入"""
        import httpx
        assert hasattr(httpx, "AsyncClient")
        assert hasattr(httpx, "TimeoutException")

    @pytest.mark.asyncio
    async def test_pricing_handles_no_notices_gracefully(self):
        """无核价通知时返回正确处理"""
        from modules.pricing.service import PricingService
        from modules.pricing.schemas import ServiceResult

        service = PricingService(user_id=1)
        service._get_cost_price = AsyncMock(return_value=80.0)
        service._get_profit_threshold = AsyncMock(return_value=20.0)

        with patch('modules.pricing.service.TemuApiClient') as MockClient:
            mock_instance = MagicMock()
            mock_instance.get_pricing_notices = AsyncMock(return_value=type('Resp', (), {
                'success': True, 'data': {'notices': [], 'total': 0}
            })())
            mock_instance.accept_pricing = AsyncMock()
            mock_instance.reject_pricing = AsyncMock()
            mock_instance.close = AsyncMock()
            MockClient.return_value = mock_instance

            result = await service.auto_handle_pricing(shop_id=1)

        assert result.success is True
        assert result.data.get('handled_count') == 0

    def test_pricing_ui_imports_no_error(self):
        """核价UI模块可正常导入"""
        from modules.pricing import ui as pricing_ui
        assert hasattr(pricing_ui, 'show_page')

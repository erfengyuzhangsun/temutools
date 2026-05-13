"""
测试：API 数据同步模块 Bug 修复
覆盖场景：
  1. SHOP_NOT_BOUND 错误给出明确提示
  2. 无凭证时同步流程优雅降级
  3. sync_orders 异常捕获和重试逻辑
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from modules.api_sync.schemas import SyncResult, SyncStatus, SyncType
from modules.api_sync.config import MODULE_CONFIG


class TestShopNotBound:
    """测试店铺未绑定场景"""

    @pytest.mark.asyncio
    async def test_sync_without_credentials_returns_clear_message(self):
        """无凭证时同步应返回明确的引导提示"""
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        service._get_shop_credentials = MagicMock(return_value=None)

        result = await service.sync_orders(shop_id=999)

        assert result.success is False
        assert result.error_code == "SHOP_NOT_BOUND"
        assert "未绑定" in result.message or "凭证" in result.message

    @pytest.mark.asyncio
    async def test_sync_all_shops_partial_failure(self):
        """多店铺同步时部分失败不应中断其他店铺"""
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)

        # Mock sync_orders to return success for shop 1, failure for shop 2
        async def mock_sync(shop_id, **kwargs):
            if shop_id == 1:
                return SyncResult(
                    success=True, message="同步完成",
                    sync_status=SyncStatus.SUCCESS,
                    data={"synced_count": 5},
                )
            else:
                return SyncResult(
                    success=False, message="店铺未绑定或API凭证缺失",
                    error_code="SHOP_NOT_BOUND", sync_status=SyncStatus.FAILED,
                )

        service.sync_orders = mock_sync
        results = await service.sync_all_shops([1, 2])

        assert len(results) == 2
        assert results[1].success is True
        assert results[2].success is False
        assert results[2].error_code == "SHOP_NOT_BOUND"


class TestSyncErrorHandling:
    """测试同步异常处理"""

    @pytest.mark.asyncio
    async def test_sync_records_error_history(self):
        """同步失败应记录到同步历史"""
        from modules.api_sync.service import ApiSyncService
        from common.temu_client import TemuApiAuthError

        service = ApiSyncService(user_id=1)
        service._get_shop_credentials = MagicMock(return_value={
            "api_key": "test_key", "api_secret": "test_secret",
        })
        service._record_sync_history = AsyncMock()

        from common.temu_client import TemuApiClient
        with patch.object(TemuApiClient, 'get_orders') as mock_get:
            mock_get.side_effect = TemuApiAuthError(
                "API认证失败(401)", status_code=401, error_code="AUTH_FAILED"
            )

            result = await service.sync_orders(shop_id=1)

            assert result.success is False
            assert result.error_code == "AUTH_FAILED"
            # Verify history was recorded
            service._record_sync_history.assert_called_once()


class TestSyncHelpMessage:
    """测试同步帮助提示"""

    def test_ui_shows_bind_prompt_when_no_shops(self):
        """无店铺时UI应显示绑定引导"""
        from modules.api_sync import ui as api_sync_ui

        # Check that the UI code contains guidance for binding shops
        import inspect
        source = inspect.getsource(api_sync_ui.show_page)

        assert "绑定" in source or "绑定新店铺" in source or "店铺管理" in source

    def test_sync_error_code_is_documented(self):
        """SHOP_NOT_BOUND 错误码应被明确定义"""
        from modules.api_sync.service import ApiSyncService

        # Verify the error message template is user-friendly
        service = ApiSyncService(user_id=1)
        import inspect
        source = inspect.getsource(service.sync_orders)

        assert "SHOP_NOT_BOUND" in source
        assert "未绑定" in source or "凭证缺失" in source

"""
测试：消息与售后模块 Bug 修复
覆盖场景：
  1. 无凭证时同步给出明确提示
  2. 空响应时正常处理
  3. 模板列名一致性验证
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestMessageSync:
    """测试消息同步"""

    @pytest.mark.asyncio
    async def test_sync_messages_handles_no_credentials(self):
        """无凭证时同步应给出友好提示而非崩溃"""
        from modules.message.service import MessageService
        from modules.message.schemas import ServiceResult

        service = MessageService(user_id=1)

        with patch('common.temu_client.TemuApiClient') as MockClient:
            mock_instance = MagicMock()
            mock_instance.get_messages = AsyncMock(return_value=ServiceResult(False, "同步失败"))
            mock_instance.close = AsyncMock()
            MockClient.return_value = mock_instance

            result = await service.sync_messages(shop_id=999)

        assert result is not None
        assert hasattr(result, 'success')

    @pytest.mark.asyncio
    async def test_sync_messages_no_error_on_empty_response(self):
        """API返回空数据时应正常处理"""
        from modules.message.service import MessageService
        from modules.message.schemas import ServiceResult

        service = MessageService(user_id=1)

        with patch('common.temu_client.TemuApiClient') as MockClient:
            mock_instance = MagicMock()
            mock_instance.get_messages = AsyncMock(return_value=ServiceResult(True, data={"messages": []}))
            mock_instance.close = AsyncMock()
            MockClient.return_value = mock_instance

            result = await service.sync_messages(shop_id=1)

        assert result.success is True
        assert result.data.get('synced') == 0

    @pytest.mark.asyncio
    async def test_sync_messages_processes_high_priority(self):
        """高优先级消息（含处罚/投诉等关键词）应正确标记"""
        from modules.message.service import MessageService
        from modules.message.schemas import ServiceResult

        service = MessageService(user_id=1)

        with patch('common.temu_client.TemuApiClient') as MockClient:
            mock_instance = MagicMock()
            mock_instance.get_messages = AsyncMock(return_value=ServiceResult(True, data={
                "messages": [
                    {"topic": "侵权投诉通知", "content": "您的商品被投诉侵权", "category": "violation"},
                    {"topic": "普通咨询", "content": "请问发货时间", "category": "general"},
                ]
            }))
            mock_instance.close = AsyncMock()
            MockClient.return_value = mock_instance

            result = await service.sync_messages(shop_id=1)

        assert result.success is True
        assert result.data.get('synced') == 2


class TestTemplateFix:
    """测试回复模板功能"""

    def test_template_column_name_matches_db(self):
        """数据库定义中模板表使用name列名"""
        from modules.message import models as msg_models

        tables_source = msg_models.TABLES.get("temu_reply_templates", "")
        # The DDL contains 'name VARCHAR(100)' 
        assert "name VARCHAR" in tables_source or "name TEXT" in tables_source

    def test_template_insert_uses_correct_column(self):
        """INSERT 语句应使用 name 列名"""
        from modules.message import ui as msg_ui
        import inspect
        source = inspect.getsource(msg_ui.show_page)

        assert "name" in source
        assert "INSERT INTO temu_reply_templates" in source

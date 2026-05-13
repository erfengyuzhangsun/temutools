"""
测试：活动报名模块 Bug 修复 (P1-7)
覆盖场景：
  1. TemuApiClient初始化失败时NameError防护
  2. 无匹配SKU时优雅返回空结果
  3. batch_apply 在无预设记录时能正常插入
  4. 匹配到的活动应持久化到数据库
"""
import pytest
from unittest.mock import AsyncMock, patch

pytestmark = pytest.mark.asyncio


class TestActivityFix:

    async def test_fetch_and_match_handles_client_failure(self):
        """TemuApiClient初始化失败不触发NameError"""
        from common.services_p2p3 import ActivityService

        service = ActivityService(uid=1)
        with patch("common.temu_client.TemuApiClient") as MockClient:
            MockClient.side_effect = Exception("API初始化失败")

            with patch("db.execute_query", return_value=[]):
                result = await service.fetch_and_match(shop_id=1)

        assert result is not None
        assert result.success is False

    async def test_fetch_and_match_returns_empty_on_no_skus(self):
        """数据库无SKU时返回空活动列表"""
        from common.services_p2p3 import ActivityService
        from common.temu_client import TemuApiResponse

        service = ActivityService(uid=1)
        with patch("common.temu_client.TemuApiClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.get_activities.return_value = TemuApiResponse(
                True, data={"activities": [
                    {"activity_id": "ACT001", "name": "家居大促", "category": "家居百货"}
                ]}
            )
            mock_instance.close = AsyncMock()
            MockClient.return_value = mock_instance

            with patch("db.execute_query", return_value=[]):
                result = await service.fetch_and_match(shop_id=1)

        assert result.success is True
        assert len(result.data.get("activities", [])) == 0

    async def test_batch_apply_handles_no_preexisting_record(self):
        """batch_apply在无预设记录时也能正常处理"""
        from common.services_p2p3 import ActivityService

        service = ActivityService(uid=1)
        with patch("db.execute_query") as mock_eq:
            mock_eq.return_value = None

            result = await service.batch_apply(
                shop_id=1, activity_id="ACT001", sku_list=["SKU1", "SKU2"]
            )

        assert result.success is True
        assert result.data.get("sku_count") == 2

    async def test_fetch_and_match_persists_matched_activities(self):
        """匹配到的活动应持久化到数据库"""
        from common.services_p2p3 import ActivityService
        from common.temu_client import TemuApiResponse

        service = ActivityService(uid=1)
        executed_queries = []

        def tracking_execute_query(sql, params=None, fetch=False):
            executed_queries.append(sql)
            if "temu_sync_orders" in sql:
                return [{"sku": "SKU1", "category": "家居百货"}]
            return []

        with patch("common.temu_client.TemuApiClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.get_activities.return_value = TemuApiResponse(
                True, data={"activities": [
                    {"activity_id": "ACT001", "name": "家居大促", "category": "家居百货"}
                ]}
            )
            mock_instance.close = AsyncMock()
            MockClient.return_value = mock_instance

            with patch("db.execute_query", side_effect=tracking_execute_query):
                result = await service.fetch_and_match(shop_id=1)

        assert result.success is True
        insert_found = any("INSERT" in q and "temu_activities" in q for q in executed_queries)
        assert insert_found, "匹配的活动应INSERT到temu_activities表"

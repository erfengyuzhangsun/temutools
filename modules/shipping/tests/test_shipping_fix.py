"""
测试：标签与发货模块 Bug 修复 (P2-8)
覆盖场景：
  1. SKU在数据库中不存在时返回0张标签（不崩溃）
  2. SKU格式清洗（前后空白字符）
  3. 混合有效/无效SKU时正确统计
  4. 空SKU列表被正确处理
"""
import pytest
from unittest.mock import AsyncMock, patch

pytestmark = pytest.mark.asyncio


class TestShippingFix:

    async def test_generate_labels_returns_zero_when_sku_not_found(self):
        """SKU在数据库中不存在时应返回0张标签（不崩溃）"""
        from common.services_p2p3 import ShippingService

        service = ShippingService(uid=1)
        with patch("db.execute_query", return_value=[]):
            result = await service.generate_labels(shop_id=1, sku_list=["NONEXISTENT_SKU"])

        assert result.success is True
        assert result.data.get("count") == 0
        assert len(result.data.get("labels", [])) == 0
        assert "NONEXISTENT_SKU" in result.data.get("skipped", [])

    async def test_generate_labels_ignores_blank_skus(self):
        """空白SKU应被自动过滤"""
        from common.services_p2p3 import ShippingService

        service = ShippingService(uid=1)
        with patch("db.execute_query", return_value=[]):
            result = await service.generate_labels(shop_id=1, sku_list=["SKU1", "", "  ", "SKU2"])

        assert result.success is True
        assert result.data.get("count") == 0

    async def test_generate_labels_strips_whitespace(self):
        """SKU前后空白字符应被自动清理"""
        from common.services_p2p3 import ShippingService

        service = ShippingService(uid=1)
        with patch("db.execute_query") as mock_eq:
            mock_eq.return_value = [
                {"sku": "SKU1", "product_name": "测试商品", "settlement_price": 100.0}
            ]

            result = await service.generate_labels(
                shop_id=1, sku_list=["  SKU1  "]
            )

        assert result.success is True
        assert result.data.get("count") == 1

    async def test_generate_labels_handles_mixed_valid_invalid_skus(self):
        """混合有效/无效SKU时正确统计"""
        from common.services_p2p3 import ShippingService

        service = ShippingService(uid=1)

        call_count = 0

        def mock_query(sql, params=None, fetch=False):
            nonlocal call_count
            call_count += 1
            if params and len(params) >= 3:
                sku = params[2]
                if sku == "SKU_VALID":
                    return [{"sku": "SKU_VALID", "product_name": "有效商品", "settlement_price": 50.0}]
            return []

        with patch("db.execute_query", side_effect=mock_query):
            result = await service.generate_labels(
                shop_id=1, sku_list=["SKU_VALID", "SKU_INVALID"]
            )

        assert result.success is True
        assert result.data.get("count") == 1
        assert "SKU_INVALID" in result.data.get("skipped", [])

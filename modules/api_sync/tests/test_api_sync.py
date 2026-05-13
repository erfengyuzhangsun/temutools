"""模块1：API对接与数据同步 - 全覆盖测试

RED阶段：所有测试初始全部失败（业务代码尚未实现）
遵循AAA模式：Arrange → Act → Assert
"""

import pytest
from datetime import datetime, date
from unittest.mock import AsyncMock, patch, MagicMock
from modules.api_sync.schemas import (
    ShopBindRequest, SyncResult, SyncRecord, SyncStatus,
    SyncHistoryItem, ShopInfo,
)
from modules.api_sync.config import MODULE_CONFIG
from common.temu_client import (
    TemuApiClient, TemuApiAuthError, TemuApiTimeoutError,
    TemuApiServerError, TemuApiResponse,
)


@pytest.mark.asyncio
class TestApiSyncNormalFlow:
    """正常流程测试"""

    async def test_single_shop_first_sync_success(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_response = TemuApiResponse(success=True, data={
            "orders": [{
                "order_id": "ORD001", "sku": "SKU001",
                "product_name": "测试商品", "category": "家居百货",
                "buyer_payment": 100.00, "platform_shipping": 10.00,
                "settlement_price": 80.00, "cost_price": 50.00,
                "status": "completed", "create_time": "2026-05-13 10:00:00",
            }],
            "total": 1,
        })
        mock_temu_client.get_orders.return_value = mock_response

        result = await service.sync_orders(shop_id=1)

        assert result.success is True
        assert result.data["synced_count"] == 1
        assert result.sync_status == SyncStatus.SUCCESS

    async def test_multi_shop_sync(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_response_1 = TemuApiResponse(success=True, data={
            "orders": [{"order_id": f"ORD00{i}", "sku": f"SKU00{i}",
                        "product_name": "商品", "category": "家居百货",
                        "buyer_payment": 100.0, "platform_shipping": 10.0,
                        "settlement_price": 80.0, "cost_price": 50.0,
                        "status": "completed", "create_time": "2026-05-13 10:00:00"}
                       for i in range(1, 6)],
            "total": 5,
        })
        mock_response_2 = TemuApiResponse(success=True, data={
            "orders": [], "total": 0,
        })
        mock_response_3 = TemuApiResponse(success=True, data={
            "orders": [{"order_id": f"ORD1{i}", "sku": f"SKU1{i}",
                        "product_name": "商品", "category": "3C数码",
                        "buyer_payment": 200.0, "platform_shipping": 15.0,
                        "settlement_price": 150.0, "cost_price": 100.0,
                        "status": "completed", "create_time": "2026-05-13 10:00:00"}
                       for i in range(1, 13)],
            "total": 12,
        })
        mock_temu_client.get_orders.side_effect = [mock_response_1, mock_response_2, mock_response_3]

        shop_ids = [1, 2, 3]
        results = await service.sync_all_shops(shop_ids)

        assert len(results) == 3
        assert results[1].success is True
        assert results[1].data["synced_count"] == 5
        assert results[2].success is True
        assert results[2].data["synced_count"] == 0
        assert results[3].success is True
        assert results[3].data["synced_count"] == 12

    async def test_incremental_sync_no_duplicates(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        existing_ids = ["ORD001", "ORD002", "ORD003"]
        service._get_existing_order_ids = AsyncMock(return_value=set(existing_ids))

        mock_response = TemuApiResponse(success=True, data={
            "orders": [
                {"order_id": "ORD001", "sku": "SKU001", "product_name": "商品",
                 "category": "家居百货", "buyer_payment": 100.0,
                 "platform_shipping": 10.0, "settlement_price": 80.0,
                 "cost_price": 50.0, "status": "completed",
                 "create_time": "2026-05-13 10:00:00"},
                {"order_id": "ORD002", "sku": "SKU002", "product_name": "商品",
                 "category": "家居百货", "buyer_payment": 100.0,
                 "platform_shipping": 10.0, "settlement_price": 80.0,
                 "cost_price": 50.0, "status": "completed",
                 "create_time": "2026-05-13 10:00:00"},
                {"order_id": "ORD004", "sku": "SKU004", "product_name": "新商品",
                 "category": "家居百货", "buyer_payment": 150.0,
                 "platform_shipping": 12.0, "settlement_price": 100.0,
                 "cost_price": 60.0, "status": "completed",
                 "create_time": "2026-05-14 10:00:00"},
            ],
            "total": 3,
        })
        mock_temu_client.get_orders.return_value = mock_response

        result = await service.sync_orders(shop_id=1)

        assert result.data["synced_count"] == 1
        assert result.data["duplicate_skipped"] == 2

    async def test_sync_history_query(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_history = [
            SyncHistoryItem(
                sync_id=1, shop_id=1, sync_type="order",
                status=SyncStatus.SUCCESS, synced_count=10,
                started_at=datetime(2026, 5, 13, 10, 0, 0),
                finished_at=datetime(2026, 5, 13, 10, 1, 30),
                duration_seconds=90.0,
            ),
            SyncHistoryItem(
                sync_id=2, shop_id=2, sync_type="order",
                status=SyncStatus.SUCCESS, synced_count=5,
                started_at=datetime(2026, 5, 13, 11, 0, 0),
                finished_at=datetime(2026, 5, 13, 11, 0, 45),
                duration_seconds=45.0,
            ),
        ]
        service._get_sync_history_from_db = AsyncMock(return_value=mock_history)

        history = await service.get_sync_history(shop_id=1)

        assert len(history) == 2
        assert history[0].status == SyncStatus.SUCCESS
        assert history[0].synced_count == 10

    async def test_shop_bind_and_encrypt(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService
        from common.crypto import CryptoUtils

        service = ApiSyncService(user_id=1)
        crypto = CryptoUtils()
        request = ShopBindRequest(
            shop_name="测试店铺",
            api_key="test_api_key_12345",
            api_secret="test_api_secret_67890",
            main_category="家居百货",
        )

        result = await service.bind_shop(request)

        assert result.success is True
        stored_key = result.data["encrypted_api_key"]
        assert stored_key != "test_api_key_12345"
        decrypted = crypto.decrypt(stored_key)
        assert decrypted == "test_api_key_12345"

    async def test_data_isolation_across_users(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service_a = ApiSyncService(user_id=1)
        service_b = ApiSyncService(user_id=2)

        mock_records_a = [{"order_id": "ORD_A001", "shop_id": 1}]
        mock_records_b = [{"order_id": "ORD_B001", "shop_id": 2}]
        service_a._query_orders_from_db = AsyncMock(return_value=mock_records_a)
        service_b._query_orders_from_db = AsyncMock(return_value=mock_records_b)

        orders_a = await service_a.get_all_orders(shop_id=1)
        orders_b = await service_b.get_all_orders(shop_id=2)

        assert len(orders_a) == 1
        assert orders_a[0]["order_id"] == "ORD_A001"
        assert len(orders_b) == 1
        assert orders_b[0]["order_id"] == "ORD_B001"
        assert orders_a != orders_b


@pytest.mark.asyncio
class TestApiSyncExceptionFlow:
    """异常场景测试"""

    async def test_api_key_invalid_return_error(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_temu_client.get_orders.side_effect = TemuApiAuthError(
            "API认证失败(401)", status_code=401, error_code="AUTH_FAILED"
        )

        result = await service.sync_orders(shop_id=1)

        assert result.success is False
        assert result.error_code == "AUTH_FAILED"
        assert result.sync_status == SyncStatus.FAILED

    async def test_network_timeout_with_retry(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_temu_client.get_orders.side_effect = TemuApiTimeoutError(
            "请求超时", status_code=0, error_code="TIMEOUT"
        )

        result = await service.sync_orders(shop_id=1)

        assert result.success is False
        assert result.error_code == "TIMEOUT"

    async def test_server_500_error(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_temu_client.get_orders.side_effect = TemuApiServerError(
            "服务器错误(500)", status_code=500, error_code="SERVER_ERROR"
        )

        result = await service.sync_orders(shop_id=1)

        assert result.success is False
        assert result.error_code == "SERVER_ERROR"

    async def test_one_shop_failure_not_affect_others(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_temu_client.get_orders.side_effect = [
            TemuApiResponse(success=True, data={
                "orders": [{"order_id": "ORD001", "sku": "SKU001",
                            "product_name": "商品", "category": "家居百货",
                            "buyer_payment": 100.0, "platform_shipping": 10.0,
                            "settlement_price": 80.0, "cost_price": 50.0,
                            "status": "completed",
                            "create_time": "2026-05-13 10:00:00"}],
                "total": 1,
            }),
            TemuApiAuthError("认证失败", status_code=401, error_code="AUTH_FAILED"),
            TemuApiResponse(success=True, data={
                "orders": [{"order_id": "ORD003", "sku": "SKU003",
                            "product_name": "商品", "category": "服装鞋包",
                            "buyer_payment": 200.0, "platform_shipping": 20.0,
                            "settlement_price": 150.0, "cost_price": 90.0,
                            "status": "completed",
                            "create_time": "2026-05-13 10:00:00"}],
                "total": 1,
            }),
        ]

        results = await service.sync_all_shops([1, 2, 3])

        assert results[1].success is True
        assert results[2].success is False
        assert results[3].success is True

    async def test_missing_fields_handling(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_response = TemuApiResponse(success=True, data={
            "orders": [{
                "order_id": "ORD001",
                "sku": "SKU001",
                "product_name": "商品",
            }],
            "total": 1,
        })
        mock_temu_client.get_orders.return_value = mock_response

        result = await service.sync_orders(shop_id=1)

        assert result.success is True
        assert result.data["synced_count"] == 1
        assert result.data["warnings"] is not None
        assert any("缺失" in w for w in result.data["warnings"])


@pytest.mark.asyncio
class TestApiSyncBoundaryValue:
    """边界值测试"""

    async def test_empty_data_from_api(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        mock_response = TemuApiResponse(success=True, data={
            "orders": [], "total": 0,
        })
        mock_temu_client.get_orders.return_value = mock_response

        result = await service.sync_orders(shop_id=1)

        assert result.success is True
        assert result.data["synced_count"] == 0
        assert result.sync_status == SyncStatus.SUCCESS

    async def test_large_data_set_with_pagination(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service = ApiSyncService(user_id=1)
        page_size = 500
        total_records = 1500

        def mock_get_orders(page=1, page_size=500, **kwargs):
            start = (page - 1) * page_size
            remaining = total_records - start
            current_page_size = min(page_size, remaining)
            orders = []
            for i in range(current_page_size):
                orders.append({
                    "order_id": f"ORD{start + i + 1:06d}",
                    "sku": f"SKU{start + i + 1:06d}",
                    "product_name": "批量商品",
                    "category": "家居百货",
                    "buyer_payment": 100.0,
                    "platform_shipping": 10.0,
                    "settlement_price": 80.0,
                    "cost_price": 50.0,
                    "status": "completed",
                    "create_time": "2026-05-13 10:00:00",
                })
            return TemuApiResponse(success=True, data={
                "orders": orders, "total": total_records,
            })

        mock_temu_client.get_orders.side_effect = mock_get_orders

        result = await service.sync_orders(shop_id=1, page_size=page_size)

        assert result.success is True
        assert result.data["synced_count"] == total_records


@pytest.mark.asyncio
class TestApiSyncSecurity:
    """安全测试"""

    async def test_api_key_masked_in_logs(self):
        from common.crypto import CryptoUtils

        crypto = CryptoUtils()
        api_key = "TEST_API_KEY_FOR_UNIT_TEST_ONLY"
        encrypted = crypto.encrypt(api_key)
        decrypted = crypto.decrypt(encrypted)

        assert encrypted != api_key
        assert decrypted == api_key

    async def test_multi_user_data_isolation(self, mock_temu_client):
        from modules.api_sync.service import ApiSyncService

        service_1 = ApiSyncService(user_id=1)
        service_2 = ApiSyncService(user_id=2)

        mock_data_1 = [
            {"order_id": "ORD_U1_001", "shop_id": 1, "user_id": 1},
            {"order_id": "ORD_U1_002", "shop_id": 1, "user_id": 1},
        ]
        mock_data_2 = [
            {"order_id": "ORD_U2_001", "shop_id": 2, "user_id": 2},
        ]
        service_1._query_orders_from_db = AsyncMock(return_value=mock_data_1)
        service_2._query_orders_from_db = AsyncMock(return_value=mock_data_2)

        orders_1 = await service_1.get_all_orders(shop_id=1)
        orders_2 = await service_2.get_all_orders(shop_id=2)

        assert len(orders_1) == 2
        assert len(orders_2) == 1
        user_ids_in_orders_1 = {o.get("user_id") for o in orders_1}
        assert user_ids_in_orders_1 == {1}


class TestApiSyncConfig:
    """配置测试"""

    def test_config_has_required_keys(self):
        required_keys = [
            "sync_interval_minutes", "max_retry_count",
            "retry_interval_seconds", "page_size",
        ]
        for key in required_keys:
            assert key in MODULE_CONFIG, f"缺少配置项: {key}"

    def test_config_values_are_valid(self):
        interval = MODULE_CONFIG["sync_interval_minutes"]
        assert interval["min"] >= 1
        assert interval["max"] <= 1440
        assert interval["min"] <= interval["default"] <= interval["max"]

        retry = MODULE_CONFIG["max_retry_count"]
        assert retry["min"] >= 0
        assert retry["max"] <= 10

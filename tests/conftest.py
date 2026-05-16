import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import AsyncGenerator, Generator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("DB_MODE", "mysql")
os.environ["ENCRYPTION_KEY"] = "test-encryption-key-for-testing-only-32chars"
os.environ["SEED_ADMIN_PASSWORD"] = "test-seed-pwd"


@pytest.fixture
def mock_temu_client():
    with patch("common.temu_client.TemuApiClient") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_order_data():
    return {
        "order_id": "ORD202605130001",
        "sku": "SKU-TEST-001",
        "product_name": "测试商品A",
        "category": "家居百货",
        "quantity": 2,
        "buyer_payment": 199.00,
        "platform_shipping": 15.00,
        "settlement_price": 120.00,
        "cost_price": 80.00,
        "status": "completed",
        "create_time": "2026-05-13 10:00:00",
        "ship_time": "2026-05-14 10:00:00",
        "confirm_time": "2026-05-18 10:00:00",
        "return_status": "",
        "store_score": 4.8,
    }


@pytest.fixture
def sample_order_list(sample_order_data):
    orders = []
    for i in range(5):
        order = sample_order_data.copy()
        order["order_id"] = f"ORD20260513000{i+1}"
        order["sku"] = f"SKU-TEST-00{i+1}"
        orders.append(order)
    return orders


@pytest.fixture
def user_shop_context():
    return {"user_id": 1, "shop_id": 1}


class MockDbCursor:
    def __init__(self, return_data=None):
        self.return_data = return_data or []
        self.executed_queries = []

    def execute(self, query, params=None):
        self.executed_queries.append((query, params))
        return self

    def fetchall(self):
        return self.return_data

    def fetchone(self):
        return self.return_data[0] if self.return_data else None

    def close(self):
        pass


@pytest.fixture
def mock_db():
    with patch("db.get_connection") as mock_conn:
        conn = MagicMock()
        cursor = MockDbCursor()
        conn.cursor.return_value = cursor
        conn.__enter__.return_value = conn
        mock_conn.return_value = conn
        yield {"conn": conn, "cursor": cursor}

import os
import sys
import pytest
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
from cryptography.fernet import Fernet

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_db_path = _db_file.name
_db_file.close()

os.environ["DB_MODE"] = "sqlite"
os.environ["SQLITE_PATH"] = _db_path
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()


def pytest_unconfigure(config):
    if os.path.exists(_db_path):
        try:
            os.unlink(_db_path)
        except Exception:
            pass


@pytest.fixture(autouse=True)
def _init_test_db():
    from db import initialize_database
    from modules.api_sync.models import initialize_sync_tables
    initialize_database()
    initialize_sync_tables()

    from db import execute_query, get_or_create_shop
    from common.crypto import CryptoUtils
    crypto = CryptoUtils()

    shop_id_1 = get_or_create_shop(1, "默认店铺", "家居百货")
    execute_query(
        "INSERT OR REPLACE INTO temu_shop_credentials "
        "(user_id, shop_id, encrypted_api_key, encrypted_api_secret) "
        "VALUES (?, ?, ?, ?)",
        (1, shop_id_1, crypto.encrypt("test_api_key_001"), crypto.encrypt("test_api_secret_001")),
    )
    shop_id_2 = get_or_create_shop(1, "测试店铺2", "3C数码")
    execute_query(
        "INSERT OR REPLACE INTO temu_shop_credentials "
        "(user_id, shop_id, encrypted_api_key, encrypted_api_secret) "
        "VALUES (?, ?, ?, ?)",
        (1, shop_id_2, crypto.encrypt("test_api_key_002"), crypto.encrypt("test_api_secret_002")),
    )
    shop_id_3 = get_or_create_shop(1, "测试店铺3", "服装鞋包")
    execute_query(
        "INSERT OR REPLACE INTO temu_shop_credentials "
        "(user_id, shop_id, encrypted_api_key, encrypted_api_secret) "
        "VALUES (?, ?, ?, ?)",
        (1, shop_id_3, crypto.encrypt("test_api_key_003"), crypto.encrypt("test_api_secret_003")),
    )
    shop_ids = {"shop_1": shop_id_1, "shop_2": shop_id_2, "shop_3": shop_id_3}

    yield shop_ids

    tables = ["temu_sync_orders", "temu_sync_history", "temu_shop_credentials",
              "temu_sku_profit", "temu_profit_stats", "temu_risk_metrics", "temu_orders"]
    for table in tables:
        try:
            execute_query(f"DELETE FROM {table}")
        except Exception:
            pass


@pytest.fixture
def mock_temu_client():
    with patch("modules.api_sync.service.TemuApiClient") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


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

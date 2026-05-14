import os
import sys
import pytest
import tempfile
from unittest.mock import AsyncMock, patch
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
os.environ["SEED_ADMIN_PASSWORD"] = "test-seed-pwd"


def pytest_unconfigure(config):
    if os.path.exists(_db_path):
        try:
            os.unlink(_db_path)
        except Exception:
            pass


@pytest.fixture(autouse=True)
def _init_test_db():
    from db import initialize_database
    from modules.pricing.models import initialize_pricing_tables
    initialize_database()
    initialize_pricing_tables()
    yield
    tables = ["temu_pricing_logs", "temu_pricing_config",
              "temu_sku_profit", "temu_profit_stats"]
    for table in tables:
        try:
            from db import execute_query
            execute_query(f"DELETE FROM {table}")
        except Exception:
            pass


@pytest.fixture
def mock_temu_client():
    with patch("modules.pricing.service.TemuApiClient") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client

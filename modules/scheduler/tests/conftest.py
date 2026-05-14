import os
import sys
import pytest
import tempfile
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


@pytest.fixture(autouse=True)
def _init_db():
    from db import initialize_database
    from modules.scheduler.models import initialize_scheduler_tables
    initialize_database()
    initialize_scheduler_tables()
    yield
    from db import execute_query
    for table in ["temu_scheduler_tasks", "temu_scheduler_logs"]:
        try:
            execute_query(f"DELETE FROM {table}")
        except Exception:
            pass

import os, tempfile
from cryptography.fernet import Fernet

_db_path = None

def get_test_db_path():
    global _db_path
    if _db_path is None:
        f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        _db_path = f.name
        f.close()
    return _db_path

def setup_test_env():
    db_path = get_test_db_path()
    os.environ["DB_MODE"] = "sqlite"
    os.environ["SQLITE_PATH"] = db_path
    os.environ["ENCRYPTION_KEY"] = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key().decode())

def init_all_tables():
    from db import initialize_database
    initialize_database()
    from modules.api_sync.models import initialize_sync_tables as t1
    from modules.inventory.models import initialize_tables as t2
    from modules.analysis.models import initialize_tables as t3
    from modules.pricing_adj.models import initialize_tables as t4
    from modules.finance.models import initialize_tables as t5
    from modules.scheduler.models import initialize_scheduler_tables as t6
    from modules.pricing.models import initialize_pricing_tables as t7
    for fn in [t1, t2, t3, t4, t5, t6, t7]:
        try: fn()
        except: pass

import os,sys,pytest,tempfile; from unittest.mock import AsyncMock, patch; from cryptography.fernet import Fernet
p=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..",".."))
if p not in sys.path: sys.path.insert(0,p)
os.environ["DB_MODE"]="sqlite";os.environ["SQLITE_PATH"]=tempfile.NamedTemporaryFile(suffix=".db",delete=False).name
os.environ["ENCRYPTION_KEY"]=Fernet.generate_key().decode()
@pytest.fixture(autouse=True)
def _init():
    from db import initialize_database; from modules.pricing_adj.models import initialize_tables
    initialize_database(); initialize_tables()
    yield
    from db import execute_query
    for t in["temu_price_adjustments","temu_competitor_prices"]:
        try: execute_query(f"DELETE FROM {t}")
        except: pass
@pytest.fixture
def mock_temu_client():
    with patch("common.temu_client.TemuApiClient") as m: c=AsyncMock();m.return_value=c;yield c

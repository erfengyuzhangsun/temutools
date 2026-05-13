import os,sys,pytest; from unittest.mock import AsyncMock, patch; from cryptography.fernet import Fernet
p=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..",".."))
if p not in sys.path: sys.path.insert(0,p)
os.environ["DB_MODE"]="sqlite";os.environ["SQLITE_PATH"]=":memory:";os.environ["ENCRYPTION_KEY"]=Fernet.generate_key().decode()
@pytest.fixture(autouse=True)
def _init():
    from db import initialize_database
    initialize_database()
    from db import execute_query
    execute_query("INSERT OR REPLACE INTO temu_users (user_id,access_password,wechat_nickname,plan_type,start_date,expire_date,is_active) VALUES (1,'test','测试用户','lifetime','2026-01-01','2036-01-01',1)")
    execute_query("INSERT OR REPLACE INTO temu_shops (shop_id,user_id,shop_name,main_category) VALUES (1,1,'测试店铺','家居百货')")
    yield
    for t in["temu_profit_stats","temu_inventory_alerts","temu_pricing_logs","temu_risk_metrics"]:
        try: execute_query(f"DELETE FROM {t}")
        except: pass

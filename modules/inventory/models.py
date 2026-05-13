import logging, re
from db import execute_query, get_connection, DB_MODE
logger = logging.getLogger(__name__)
def _to_sqlite_safe(sql):
    if DB_MODE == "mysql": return sql
    sql = re.sub(r"COMMENT\s*=\s*'[^']*'", "", sql); sql = re.sub(r"COMMENT\s+'[^']*'", "", sql)
    sql = re.sub(r"UNIQUE\s+KEY\s+\w+\s*", "UNIQUE ", sql); sql = re.sub(r",\s*KEY\s+\w+\s+\([^)]+\)", "", sql)
    for o, n in {"INTEGER AUTO_INCREMENT PRIMARY KEY":"INTEGER PRIMARY KEY AUTOINCREMENT","DECIMAL(10,2)":"REAL","DECIMAL(5,2)":"REAL","TINYINT(1)":"INTEGER","VARCHAR(255)":"TEXT","VARCHAR(100)":"TEXT","VARCHAR(50)":"TEXT","VARCHAR(30)":"TEXT","VARCHAR(20)":"TEXT","ENGINE=InnoDB":"","DEFAULT CHARSET=utf8mb4":"","ON UPDATE CURRENT_TIMESTAMP":""}.items():
        sql = sql.replace(o, n)
    return sql

TABLES = {
    "temu_inventory": """CREATE TABLE IF NOT EXISTS temu_inventory (
        inv_id INTEGER AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, shop_id INT NOT NULL,
        sku VARCHAR(100) NOT NULL, product_name VARCHAR(255) DEFAULT '', category VARCHAR(50) DEFAULT '',
        current_stock INT DEFAULT 0, safety_stock INT DEFAULT 0, daily_avg_sales DECIMAL(10,2) DEFAULT 0.00,
        lead_time_days INT DEFAULT 7, cost_price DECIMAL(10,2) DEFAULT 0.00, status VARCHAR(20) DEFAULT 'normal',
        last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,
        UNIQUE KEY uk_sku (user_id, shop_id, sku)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存数据';""",
    "temu_inventory_alerts": """CREATE TABLE IF NOT EXISTS temu_inventory_alerts (
        alert_id INTEGER AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, shop_id INT NOT NULL,
        sku VARCHAR(100) NOT NULL, alert_type VARCHAR(30) NOT NULL, message TEXT NOT NULL,
        is_read TINYINT(1) DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存告警';""",
}
def initialize_tables():
    for tn, sql in TABLES.items():
        try:
            c = get_connection(); cur = c.cursor(); cur.execute(_to_sqlite_safe(sql)); cur.close(); c.commit(); c.close()
        except Exception as e: logger.error(f"创建表 {tn} 失败: {e}")

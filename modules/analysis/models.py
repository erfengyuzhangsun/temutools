import logging, re; from db import execute_query, get_connection, DB_MODE; logger=logging.getLogger(__name__)
def _to_sqlite_safe(sql):
    if DB_MODE=="mysql": return sql
    sql = re.sub(r"COMMENT\s*=\s*'[^']*'", "", sql); sql = re.sub(r"COMMENT\s+'[^']*'", "", sql)
    sql = re.sub(r"UNIQUE\s+KEY\s+\w+\s*", "UNIQUE ", sql); sql = re.sub(r",\s*KEY\s+\w+\s+\([^)]+\)", "", sql)
    for o,n in {"INTEGER AUTO_INCREMENT PRIMARY KEY":"INTEGER PRIMARY KEY AUTOINCREMENT","DECIMAL(10,2)":"REAL","DECIMAL(5,2)":"REAL","TINYINT(1)":"INTEGER","VARCHAR(255)":"TEXT","VARCHAR(100)":"TEXT","VARCHAR(50)":"TEXT","VARCHAR(30)":"TEXT","VARCHAR(20)":"TEXT","ENGINE=InnoDB":"","DEFAULT CHARSET=utf8mb4":"","ON UPDATE CURRENT_TIMESTAMP":""}.items():
        sql=sql.replace(o,n)
    return sql
TABLES={
    "temu_shop_metrics":"""CREATE TABLE IF NOT EXISTS temu_shop_metrics (metric_id INTEGER AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,shop_id INT NOT NULL,record_date DATE NOT NULL,impressions INT DEFAULT 0,clicks INT DEFAULT 0,click_rate DECIMAL(5,2) DEFAULT 0.00,conversion_rate DECIMAL(5,2) DEFAULT 0.00,return_rate DECIMAL(5,2) DEFAULT 0.00,total_sales DECIMAL(10,2) DEFAULT 0.00,total_orders INT DEFAULT 0,negative_review_rate DECIMAL(5,2) DEFAULT 0.00,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,UNIQUE KEY uk_date (user_id,shop_id,record_date)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='店铺运营指标';""",
    "temu_alert_rules":"""CREATE TABLE IF NOT EXISTS temu_alert_rules (rule_id INTEGER AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,shop_id INT DEFAULT NULL,metric_key VARCHAR(50) NOT NULL,operator VARCHAR(10) NOT NULL,threshold DECIMAL(10,2) NOT NULL,enabled TINYINT(1) DEFAULT 1,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警规则';""",
}
def initialize_tables():
    for tn,sql in TABLES.items():
        try: c=get_connection();cur=c.cursor();cur.execute(_to_sqlite_safe(sql));cur.close();c.commit();c.close()
        except Exception as e: logger.error(f"创建表 {tn} 失败: {e}")

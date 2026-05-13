import logging,re; from db import execute_query, get_connection, DB_MODE; logger=logging.getLogger(__name__)
def _to_sqlite_safe(sql):
    if DB_MODE=="mysql": return sql
    sql=re.sub(r"COMMENT\s*=\s*'[^']*'","",sql);sql=re.sub(r"COMMENT\s+'[^']*'","",sql)
    sql=re.sub(r"UNIQUE\s+KEY\s+\w+\s*","UNIQUE ",sql);sql=re.sub(r",\s*KEY\s+\w+\s+\([^)]+\)","",sql)
    for o,n in {"INTEGER AUTO_INCREMENT PRIMARY KEY":"INTEGER PRIMARY KEY AUTOINCREMENT","DECIMAL(10,2)":"REAL","DECIMAL(5,2)":"REAL","TINYINT(1)":"INTEGER","VARCHAR(255)":"TEXT","VARCHAR(100)":"TEXT","VARCHAR(50)":"TEXT","VARCHAR(30)":"TEXT","VARCHAR(20)":"TEXT","ENGINE=InnoDB":"","DEFAULT CHARSET=utf8mb4":"","ON UPDATE CURRENT_TIMESTAMP":""}.items(): sql=sql.replace(o,n)
    return sql
TABLES={
    "temu_settlements":"""CREATE TABLE IF NOT EXISTS temu_settlements (settlement_id INTEGER AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,shop_id INT NOT NULL,period_start DATE NOT NULL,period_end DATE NOT NULL,total_revenue DECIMAL(10,2) DEFAULT 0.00,total_deductions DECIMAL(10,2) DEFAULT 0.00,net_payout DECIMAL(10,2) DEFAULT 0.00,status VARCHAR(20) DEFAULT 'pending',settlement_date DATE,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,UNIQUE KEY uk_period (user_id,shop_id,period_start,period_end)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='结算账单';""",
    "temu_reconciliation_logs":"""CREATE TABLE IF NOT EXISTS temu_reconciliation_logs (rec_id INTEGER AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,shop_id INT NOT NULL,settlement_id INT NOT NULL,expected_amount DECIMAL(10,2) NOT NULL,actual_amount DECIMAL(10,2) NOT NULL,difference DECIMAL(10,2) DEFAULT 0.00,status VARCHAR(20) DEFAULT 'pending',notes TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对账记录';""",
}
def initialize_tables():
    for tn,sql in TABLES.items():
        try: c=get_connection();cur=c.cursor();cur.execute(_to_sqlite_safe(sql));cur.close();c.commit();c.close()
        except Exception as e: logger.error(f"创建表 {tn} 失败: {e}")

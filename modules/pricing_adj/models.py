import logging,re; from db import execute_query, get_connection, DB_MODE; logger=logging.getLogger(__name__)
def _to_sqlite_safe(sql):
    if DB_MODE=="mysql": return sql
    sql=re.sub(r"COMMENT\s*=\s*'[^']*'","",sql);sql=re.sub(r"COMMENT\s+'[^']*'","",sql)
    sql=re.sub(r"UNIQUE\s+KEY\s+\w+\s*","UNIQUE ",sql);sql=re.sub(r",\s*KEY\s+\w+\s+\([^)]+\)","",sql)
    for o,n in {"INTEGER AUTO_INCREMENT PRIMARY KEY":"INTEGER PRIMARY KEY AUTOINCREMENT","DECIMAL(10,2)":"REAL","DECIMAL(5,2)":"REAL","TINYINT(1)":"INTEGER","VARCHAR(255)":"TEXT","VARCHAR(100)":"TEXT","VARCHAR(50)":"TEXT","VARCHAR(30)":"TEXT","VARCHAR(20)":"TEXT","ENGINE=InnoDB":"","DEFAULT CHARSET=utf8mb4":"","ON UPDATE CURRENT_TIMESTAMP":""}.items(): sql=sql.replace(o,n)
    return sql
TABLES={
    "temu_price_adjustments":"""CREATE TABLE IF NOT EXISTS temu_price_adjustments (adj_id INTEGER AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,shop_id INT NOT NULL,sku VARCHAR(100) NOT NULL,old_price DECIMAL(10,2) NOT NULL,new_price DECIMAL(10,2) NOT NULL,reason TEXT,adjustment_type VARCHAR(20) DEFAULT 'auto',operator VARCHAR(50) DEFAULT 'system',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='调价记录';""",
    "temu_competitor_prices":"""CREATE TABLE IF NOT EXISTS temu_competitor_prices (cp_id INTEGER AUTO_INCREMENT PRIMARY KEY,shop_id INT NOT NULL,sku VARCHAR(100) NOT NULL,price DECIMAL(10,2) NOT NULL,source VARCHAR(50) DEFAULT 'temu',collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='竞品价格';""",
}
def initialize_tables():
    for tn,sql in TABLES.items():
        try: c=get_connection();cur=c.cursor();cur.execute(_to_sqlite_safe(sql));cur.close();c.commit();c.close()
        except Exception as e: logger.error(f"创建表 {tn} 失败: {e}")

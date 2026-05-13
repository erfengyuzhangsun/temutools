import logging,re;from db import execute_query,get_connection,DB_MODE;logger=logging.getLogger(__name__)
def _safe(sql):
    if DB_MODE=="mysql":return sql
    sql=re.sub(r"COMMENT\s*=\s*'[^']*'","",sql);sql=re.sub(r"COMMENT\s+'[^']*'","",sql);sql=re.sub(r"UNIQUE\s+KEY\s+\w+\s*","UNIQUE ",sql);sql=re.sub(r",\s*KEY\s+\w+\s+\([^)]+\)","",sql)
    for o,n in {"INTEGER AUTO_INCREMENT PRIMARY KEY":"INTEGER PRIMARY KEY AUTOINCREMENT","DECIMAL(10,2)":"REAL","DECIMAL(5,2)":"REAL","TINYINT(1)":"INTEGER","VARCHAR(255)":"TEXT","VARCHAR(100)":"TEXT","VARCHAR(50)":"TEXT","VARCHAR(30)":"TEXT","ENGINE=InnoDB":"","DEFAULT CHARSET=utf8mb4":"","ON UPDATE CURRENT_TIMESTAMP":""}.items():sql=sql.replace(o,n)
    return sql
TABLES={
    "temu_messages":"""CREATE TABLE IF NOT EXISTS temu_messages (msg_id INTEGER AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,shop_id INT NOT NULL,topic VARCHAR(100) NOT NULL,content TEXT,priority VARCHAR(20) DEFAULT 'normal',category VARCHAR(50),is_read TINYINT(1) DEFAULT 0,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台消息';""",
    "temu_reply_templates":"""CREATE TABLE IF NOT EXISTS temu_reply_templates (tmpl_id INTEGER AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,name VARCHAR(100) NOT NULL,category VARCHAR(50),content TEXT NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回复模板';""",
}
def initialize_tables():
    for tn,sql in TABLES.items():
        try:c=get_connection();cur=c.cursor();cur.execute(_safe(sql));cur.close();c.commit();c.close()
        except Exception as e:logger.error(f"创建表 {tn} 失败: {e}")

import logging
import re
from db import execute_query, get_connection, DB_MODE

logger = logging.getLogger(__name__)


def _to_sqlite_safe(sql: str) -> str:
    if DB_MODE == "mysql":
        return sql
    sql = re.sub(r"COMMENT\s*=\s*'[^']*'", "", sql)
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql)
    replacements = {
        "INTEGER AUTO_INCREMENT PRIMARY KEY": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "TINYINT(1)": "INTEGER",
        "VARCHAR(255)": "TEXT",
        "VARCHAR(100)": "TEXT",
        "VARCHAR(50)": "TEXT",
        "ENGINE=InnoDB": "",
        "DEFAULT CHARSET=utf8mb4": "",
        "ON UPDATE CURRENT_TIMESTAMP": "",
    }
    for old, new in replacements.items():
        sql = sql.replace(old, new)
    return sql


def initialize_tables():
    sql = """
        CREATE TABLE IF NOT EXISTS temu_risk_guard_logs (
            log_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            sku_code VARCHAR(100) DEFAULT '',
            operation VARCHAR(50) NOT NULL COMMENT '操作类型',
            detail TEXT COMMENT '详情',
            risk_level VARCHAR(20) DEFAULT 'low' COMMENT '风险等级',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='风控检测日志';
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(_to_sqlite_safe(sql))
        cursor.close()
        conn.commit()
        conn.close()
        logger.info("风控日志表创建成功")
    except Exception as e:
        logger.error(f"创建风控日志表失败: {e}")

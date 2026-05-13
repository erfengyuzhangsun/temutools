import logging
import re
from db import execute_query, get_connection, DB_MODE

logger = logging.getLogger(__name__)


def _to_sqlite_safe(sql: str) -> str:
    if DB_MODE == "mysql":
        return sql
    sql = re.sub(r"COMMENT\s*=\s*'[^']*'", "", sql)
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql)
    sql = re.sub(r"UNIQUE\s+KEY\s+\w+\s*", "UNIQUE ", sql)
    sql = re.sub(r",\s*KEY\s+\w+\s+\([^)]+\)", "", sql)
    replacements = {
        "INTEGER AUTO_INCREMENT PRIMARY KEY": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "DECIMAL(10,2)": "REAL",
        "DECIMAL(5,2)": "REAL",
        "TINYINT(1)": "INTEGER",
        "VARCHAR(255)": "TEXT",
        "VARCHAR(100)": "TEXT",
        "VARCHAR(50)": "TEXT",
        "VARCHAR(30)": "TEXT",
        "VARCHAR(20)": "TEXT",
        "ENGINE=InnoDB": "",
        "DEFAULT CHARSET=utf8mb4": "",
        "ON UPDATE CURRENT_TIMESTAMP": "",
    }
    for old, new in replacements.items():
        sql = sql.replace(old, new)
    return sql


PRICING_TABLES = {
    "temu_pricing_logs": """
        CREATE TABLE IF NOT EXISTS temu_pricing_logs (
            log_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            shop_id INT NOT NULL,
            notice_id VARCHAR(100) NOT NULL COMMENT '核价通知ID',
            sku VARCHAR(100) NOT NULL COMMENT 'SKU编码',
            action VARCHAR(20) NOT NULL COMMENT '操作(accept/reject/skip)',
            supply_price DECIMAL(10,2) NOT NULL COMMENT '供货价',
            cost_price DECIMAL(10,2) NOT NULL COMMENT '成本价',
            gross_margin DECIMAL(5,2) DEFAULT 0.00 COMMENT '毛利率',
            reason TEXT DEFAULT NULL COMMENT '原因',
            is_activity TINYINT(1) DEFAULT 0 COMMENT '是否活动商品',
            handled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '处理时间',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='核价操作日志';
    """,
    "temu_pricing_config": """
        CREATE TABLE IF NOT EXISTS temu_pricing_config (
            config_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            shop_id INT DEFAULT NULL,
            profit_threshold DECIMAL(5,2) NOT NULL DEFAULT 20.00 COMMENT '毛利率阈值',
            activity_threshold DECIMAL(5,2) NOT NULL DEFAULT 10.00 COMMENT '活动毛利率阈值',
            auto_handle_enabled TINYINT(1) DEFAULT 1 COMMENT '是否自动处理',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uk_user_config (user_id, shop_id),
            FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='核价配置';
    """,
}


def initialize_pricing_tables():
    for table_name, sql in PRICING_TABLES.items():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            safe_sql = _to_sqlite_safe(sql)
            cursor.execute(safe_sql)
            cursor.close()
            conn.commit()
            conn.close()
            logger.info(f"数据表创建成功: {table_name}")
        except Exception as e:
            logger.error(f"创建表 {table_name} 失败: {e}")

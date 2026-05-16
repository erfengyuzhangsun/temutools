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
        "ENGINE=InnoDB": "",
        "DEFAULT CHARSET=utf8mb4": "",
        "ON UPDATE CURRENT_TIMESTAMP": "",
    }
    for old, new in replacements.items():
        sql = sql.replace(old, new)
    return sql


FACTORY_TABLES = {
    "temu_factory_products": """
        CREATE TABLE IF NOT EXISTS temu_factory_products (
            product_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_name VARCHAR(255) NOT NULL,
            sku_code VARCHAR(100) NOT NULL,
            category_name VARCHAR(100) DEFAULT '',
            material_cost DECIMAL(10,2) DEFAULT 0.00,
            labor_cost DECIMAL(10,2) DEFAULT 0.00,
            packaging_cost DECIMAL(10,2) DEFAULT 0.00,
            shipping_cost DECIMAL(10,2) DEFAULT 0.00,
            other_cost DECIMAL(10,2) DEFAULT 0.00,
            total_cost DECIMAL(10,2) DEFAULT 0.00,
            expected_profit_margin DECIMAL(5,2) DEFAULT 20.00,
            suggested_supply_price DECIMAL(10,2) DEFAULT 0.00,
            product_images TEXT,
            product_description TEXT,
            is_full_commission TINYINT(1) DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uk_user_sku (user_id, sku_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工厂产品成本表';
    """,
}


def initialize_tables():
    for table_name, sql in FACTORY_TABLES.items():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            safe_sql = _to_sqlite_safe(sql)
            cursor.execute(safe_sql)
            cursor.close()
            conn.commit()
            conn.close()
            logger.info(f"工厂成本表创建成功: {table_name}")
        except Exception as e:
            logger.error(f"创建表 {table_name} 失败: {e}")

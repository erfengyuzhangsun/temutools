import logging
import re
from db import execute_query, get_connection, DB_MODE

logger = logging.getLogger(__name__)


def _to_sqlite_safe(sql: str) -> str:
    if DB_MODE == "mysql":
        return sql
    sql = re.sub(r"COMMENT\s*=\s*'[^']*'", "", sql)
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql)
    sql = re.sub(r"COMMENT\s*=\s*\"[^\"]*\"", "", sql)
    sql = re.sub(r"COMMENT\s+\"[^\"]*\"", "", sql)
    sql = re.sub(r"UNIQUE\s+KEY\s+\w+\s*", "UNIQUE ", sql)
    sql = re.sub(r"FOREIGN\s+KEY\s+\((\w+)\)", r"FOREIGN KEY (\1)", sql)
    sql = re.sub(r",\s*KEY\s+\w+\s+\([^)]+\)", "", sql)
    replacements = {
        "INTEGER AUTO_INCREMENT PRIMARY KEY": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "INT AUTO_INCREMENT PRIMARY KEY": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "TINYINT(1)": "INTEGER",
        "TINYINT": "INTEGER",
        "DECIMAL(10,2)": "REAL",
        "DECIMAL(5,2)": "REAL",
        "DECIMAL(5,1)": "REAL",
        "DECIMAL(3,1)": "REAL",
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


SYNC_TABLES = {
    "temu_shop_credentials": """
        CREATE TABLE IF NOT EXISTS temu_shop_credentials (
            cred_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            shop_id INT NOT NULL,
            encrypted_api_key TEXT NOT NULL COMMENT '加密API Key',
            encrypted_api_secret TEXT NOT NULL COMMENT '加密API Secret',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,
            UNIQUE KEY uk_user_shop (user_id, shop_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='店铺API凭证加密存储';
    """,
    "temu_sync_orders": """
        CREATE TABLE IF NOT EXISTS temu_sync_orders (
            sync_order_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            shop_id INT NOT NULL,
            order_id VARCHAR(100) NOT NULL COMMENT '平台订单ID',
            sku VARCHAR(100) NOT NULL COMMENT 'SKU编码',
            product_name VARCHAR(255) DEFAULT '' COMMENT '商品名称',
            category VARCHAR(50) DEFAULT '家居百货' COMMENT '类目',
            buyer_payment DECIMAL(10,2) DEFAULT 0.00 COMMENT '买家支付金额',
            platform_shipping DECIMAL(10,2) DEFAULT 0.00 COMMENT '平台运费',
            settlement_price DECIMAL(10,2) DEFAULT 0.00 COMMENT '结算价',
            cost_price DECIMAL(10,2) DEFAULT 0.00 COMMENT '成本价',
            status VARCHAR(20) DEFAULT 'pending' COMMENT '订单状态',
            quantity INT DEFAULT 1 COMMENT '数量',
            create_time VARCHAR(50) DEFAULT NULL COMMENT '创建时间',
            ship_time VARCHAR(50) DEFAULT NULL COMMENT '发货时间',
            confirm_time VARCHAR(50) DEFAULT NULL COMMENT '确认收货时间',
            return_status VARCHAR(20) DEFAULT '' COMMENT '退货状态',
            store_score DECIMAL(3,1) DEFAULT 4.8 COMMENT '店铺评分',
            raw_data TEXT DEFAULT NULL COMMENT '原始JSON数据',
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '同步时间',
            FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,
            UNIQUE KEY uk_order (user_id, shop_id, order_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='同步订单数据';
    """,
    "temu_sync_history": """
        CREATE TABLE IF NOT EXISTS temu_sync_history (
            sync_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            shop_id INT NOT NULL,
            sync_type VARCHAR(30) NOT NULL COMMENT '同步类型',
            status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态',
            synced_count INT DEFAULT 0 COMMENT '同步数量',
            record_count INT DEFAULT 0 COMMENT '记录总数',
            error_message TEXT DEFAULT NULL COMMENT '错误信息',
            duration_seconds DECIMAL(10,2) DEFAULT 0.00 COMMENT '耗时',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
            finished_at TIMESTAMP NULL DEFAULT NULL COMMENT '结束时间',
            FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,
            KEY idx_user_shop (user_id, shop_id),
            KEY idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='同步历史记录';
    """,
}


def initialize_sync_tables():
    for table_name, sql in SYNC_TABLES.items():
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

import os
import sqlite3
import pandas as pd

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    mysql = None
    MYSQL_AVAILABLE = False
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Tuple, Any
from contextlib import contextmanager

DB_MODE = os.environ.get("DB_MODE", "sqlite").lower()

SQLITE_PATH = os.environ.get("SQLITE_PATH", "temu_tools.db")

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "temu_tools"),
}

try:
    import streamlit as st
    if hasattr(st, "secrets") and "mysql" in st.secrets:
        mysql_cfg = st.secrets["mysql"]
        MYSQL_CONFIG["host"] = mysql_cfg.get("host", MYSQL_CONFIG["host"])
        MYSQL_CONFIG["port"] = int(mysql_cfg.get("port", MYSQL_CONFIG["port"]))
        MYSQL_CONFIG["user"] = mysql_cfg.get("user", MYSQL_CONFIG["user"])
        MYSQL_CONFIG["password"] = mysql_cfg.get("password", MYSQL_CONFIG["password"])
        MYSQL_CONFIG["database"] = mysql_cfg.get("database", MYSQL_CONFIG["database"])
except Exception:
    pass


def get_connection():
    if DB_MODE == "mysql":
        if not MYSQL_AVAILABLE:
            raise ImportError("MySQL 连接器未安装，请执行: pip install mysql-connector-python")
        return mysql.connector.connect(**MYSQL_CONFIG)
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn


def execute_query(query: str, params: tuple = None, fetch: bool = False):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True) if DB_MODE == "mysql" else conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if fetch:
            if DB_MODE == "sqlite":
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            return cursor.fetchall()
        conn.commit()
        return cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


import re

def adapt_query_for_sqlite(query: str) -> str:
    if DB_MODE == "sqlite":
        query = re.sub(r"COMMENT\s+'[^']*'", "", query)
        query = re.sub(r"COMMENT\s+\"[^\"]*\"", "", query)
        query = re.sub(r"UNIQUE\s+KEY\s+\w+\s*", "UNIQUE ", query)
        query = re.sub(r"FOREIGN\s+KEY\s+\((\w+)\)", r"FOREIGN KEY (\1)", query)
        query = re.sub(r"ENUM\s*\([^)]*\)", "TEXT", query)

        replacements = {
            "INTEGER AUTO_INCREMENT PRIMARY KEY": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "INT AUTO_INCREMENT PRIMARY KEY": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "TINYINT(1)": "INTEGER",
            "TINYINT": "INTEGER",
            "DECIMAL(10,2)": "REAL",
            "DECIMAL(5,2)": "REAL",
            "DECIMAL(5,1)": "REAL",
            "VARCHAR(255)": "TEXT",
            "VARCHAR(100)": "TEXT",
            "VARCHAR(50)": "TEXT",
            "ENGINE=InnoDB": "",
            "DEFAULT CHARSET=utf8mb4": "",
            "ON UPDATE CURRENT_TIMESTAMP": "",
        }
        for old, new in replacements.items():
            query = query.replace(old, new)
    return query


def initialize_database():
    if DB_MODE == "mysql":
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET utf8mb4")
        cursor.close()
        conn.close()

    tables_sql = get_table_schemas()
    for table_name, sql in tables_sql.items():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(adapt_query_for_sqlite(sql) if DB_MODE == "sqlite" else sql)
            cursor.close()
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"创建表 {table_name} 时出错: {e}")

    if DB_MODE == "sqlite":
        ensure_sqlite_defaults()


def get_table_schemas():
    return {
        "temu_users": """
            CREATE TABLE IF NOT EXISTS temu_users (
                user_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                access_password VARCHAR(255) NOT NULL COMMENT '用户访问密码',
                wechat_nickname VARCHAR(100) NOT NULL COMMENT '微信昵称',
                plan_type ENUM('basic', 'pro', 'lifetime') NOT NULL COMMENT '套餐类型',
                start_date DATE NOT NULL COMMENT '付费开始日期',
                expire_date DATE NOT NULL COMMENT '到期日期',
                is_active TINYINT(1) DEFAULT 1 COMMENT '是否有效',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_access_password (access_password)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        "temu_shops": """
            CREATE TABLE IF NOT EXISTS temu_shops (
                shop_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                shop_name VARCHAR(100) NOT NULL COMMENT '店铺名称',
                main_category VARCHAR(50) COMMENT '主营类目',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
                UNIQUE KEY uk_user_shop (user_id, shop_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        "temu_profit_stats": """
            CREATE TABLE IF NOT EXISTS temu_profit_stats (
                stat_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                shop_id INT NOT NULL,
                stat_date DATE NOT NULL COMMENT '统计日期',
                total_orders INT NOT NULL DEFAULT 0,
                total_revenue DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_commission DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_payment_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_performance_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_return_loss DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_shipping_penalty DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_profit DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                net_profit_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,
                UNIQUE KEY uk_user_shop_date (user_id, shop_id, stat_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        "temu_sku_profit": """
            CREATE TABLE IF NOT EXISTS temu_sku_profit (
                sku_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                shop_id INT NOT NULL,
                sku_code VARCHAR(100) NOT NULL COMMENT 'SKU编码',
                sku_name VARCHAR(255) NOT NULL COMMENT 'SKU名称',
                category VARCHAR(50) NOT NULL COMMENT '类目',
                cost_price DECIMAL(10,2) NOT NULL COMMENT '供货成本',
                total_sales INT NOT NULL DEFAULT 0,
                total_revenue DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_profit DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                profit_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                is_loss TINYINT(1) DEFAULT 0 COMMENT '是否亏损',
                is_warning TINYINT(1) DEFAULT 0 COMMENT '是否预警',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,
                UNIQUE KEY uk_user_shop_sku (user_id, shop_id, sku_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
        "temu_risk_metrics": """
            CREATE TABLE IF NOT EXISTS temu_risk_metrics (
                metric_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                shop_id INT NOT NULL,
                record_date DATE NOT NULL,
                delivery_overdue_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                fake_delivery_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                wrong_product_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                out_of_stock_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                return_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                bad_review_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                comprehensive_score DECIMAL(5,1) NOT NULL DEFAULT 100.0,
                predicted_fine DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES temu_users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (shop_id) REFERENCES temu_shops(shop_id) ON DELETE CASCADE,
                UNIQUE KEY uk_user_shop_date (user_id, shop_id, record_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """,
    }


def ensure_sqlite_defaults():
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM temu_users")
    count = cursor.fetchone()[0]
    if count == 0:
        today = date.today()
        expire = today + timedelta(days=365 * 10)
        cursor.execute(
            "INSERT INTO temu_users (access_password, wechat_nickname, plan_type, start_date, expire_date, is_active) VALUES (?, ?, ?, ?, ?, 1)",
            ("admin123", "管理员", "lifetime", today.isoformat(), expire.isoformat())
        )
        admin_user_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO temu_shops (user_id, shop_name, main_category) VALUES (?, ?, ?)",
            (admin_user_id, "默认店铺", "家居百货")
        )
    conn.commit()
    conn.close()


def verify_user_password(password: str) -> Optional[Dict]:
    users = execute_query(
        "SELECT user_id, wechat_nickname, plan_type, start_date, expire_date, is_active FROM temu_users WHERE access_password = ? AND is_active = 1",
        (password,),
        fetch=True
    )
    if not users:
        return None
    user = users[0]
    if isinstance(user.get('expire_date'), str):
        user['expire_date'] = datetime.strptime(user['expire_date'], '%Y-%m-%d').date()
    if isinstance(user.get('start_date'), str):
        user['start_date'] = datetime.strptime(user['start_date'], '%Y-%m-%d').date()
    today = date.today()
    if user['expire_date'] < today:
        return {"error": "expired"}
    return user


def get_or_create_shop(user_id: int, shop_name: str = "默认店铺", main_category: str = "家居百货") -> int:
    shops = execute_query(
        "SELECT shop_id FROM temu_shops WHERE user_id = ? AND shop_name = ?",
        (user_id, shop_name),
        fetch=True
    )
    if shops:
        return shops[0]['shop_id']
    return execute_query(
        "INSERT INTO temu_shops (user_id, shop_name, main_category) VALUES (?, ?, ?)",
        (user_id, shop_name, main_category)
    )


def save_profit_stats(user_id: int, shop_id: int, summary: Dict):
    stat_date = date.today()
    existing = execute_query(
        "SELECT stat_id FROM temu_profit_stats WHERE user_id = ? AND shop_id = ? AND stat_date = ?",
        (user_id, shop_id, stat_date.isoformat()),
        fetch=True
    )
    data = (
        user_id, shop_id, stat_date.isoformat(),
        summary.get('total_orders', 0),
        summary.get('total_revenue', 0),
        summary.get('total_cost', 0),
        summary.get('total_commission', 0),
        summary.get('total_payment_fee', 0),
        summary.get('total_performance_fee', 0),
        summary.get('total_return_loss', 0),
        summary.get('total_shipping_penalty', 0),
        summary.get('total_profit', 0),
        summary.get('net_profit_rate', 0),
    )
    if existing:
        execute_query(
            """UPDATE temu_profit_stats SET total_orders=?, total_revenue=?, total_cost=?,
               total_commission=?, total_payment_fee=?, total_performance_fee=?,
               total_return_loss=?, total_shipping_penalty=?, total_profit=?, net_profit_rate=?
               WHERE user_id=? AND shop_id=? AND stat_date=?""",
            data[3:] + (user_id, shop_id, stat_date.isoformat())
        )
    else:
        execute_query(
            """INSERT INTO temu_profit_stats
               (user_id, shop_id, stat_date, total_orders, total_revenue, total_cost,
                total_commission, total_payment_fee, total_performance_fee,
                total_return_loss, total_shipping_penalty, total_profit, net_profit_rate)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data
        )


def save_sku_profits(user_id: int, shop_id: int, sku_df: pd.DataFrame):
    for _, row in sku_df.iterrows():
        sku_code = str(row.get('SKU', ''))
        sku_name = str(row.get('商品名称', ''))
        category = str(row.get('类目', ''))
        cost_price = float(row.get('总成本', row.get('成本价', 0)))
        total_sales = int(row.get('销量', row.get('订单数', 0)))
        total_revenue = float(row.get('销售额', row.get('买家支付', 0)))
        total_profit = float(row.get('总利润', row.get('利润', 0)))
        profit_rate = float(row.get('利润率', row.get('利润率%', 0)))
        is_loss = 1 if total_profit < 0 else 0
        is_warning = 1 if profit_rate < 5 else 0

        existing = execute_query(
            "SELECT sku_id FROM temu_sku_profit WHERE user_id = ? AND shop_id = ? AND sku_code = ?",
            (user_id, shop_id, sku_code),
            fetch=True
        )
        if existing:
            execute_query(
                """UPDATE temu_sku_profit SET sku_name=?, category=?, cost_price=?,
                   total_sales=?, total_revenue=?, total_profit=?, profit_rate=?,
                   is_loss=?, is_warning=?, last_updated=CURRENT_TIMESTAMP
                   WHERE user_id=? AND shop_id=? AND sku_code=?""",
                (sku_name, category, cost_price, total_sales, total_revenue,
                 total_profit, profit_rate, is_loss, is_warning,
                 user_id, shop_id, sku_code)
            )
        else:
            execute_query(
                """INSERT INTO temu_sku_profit
                   (user_id, shop_id, sku_code, sku_name, category, cost_price,
                    total_sales, total_revenue, total_profit, profit_rate, is_loss, is_warning)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, shop_id, sku_code, sku_name, category, cost_price,
                 total_sales, total_revenue, total_profit, profit_rate, is_loss, is_warning)
            )


def save_risk_metrics(user_id: int, shop_id: int, risk_report: Dict):
    record_date = date.today()
    indicators = {item['指标名称']: item for item in risk_report.get('详细指标', [])}

    def parse_rate(val_str: str) -> float:
        try:
            return float(val_str.replace('%', ''))
        except (ValueError, AttributeError):
            return 0.0

    existing = execute_query(
        "SELECT metric_id FROM temu_risk_metrics WHERE user_id = ? AND shop_id = ? AND record_date = ?",
        (user_id, shop_id, record_date.isoformat()),
        fetch=True
    )
    data = (
        user_id, shop_id, record_date.isoformat(),
        parse_rate(indicators.get('发货超时率', {}).get('当前值', '0%')),
        parse_rate(indicators.get('虚假发货率', {}).get('当前值', '0%')),
        parse_rate(indicators.get('货不对版率', {}).get('当前值', '0%')),
        parse_rate(indicators.get('缺货率', {}).get('当前值', '0%')),
        parse_rate(indicators.get('退货率', {}).get('当前值', '0%')),
        parse_rate(indicators.get('差评率', {}).get('当前值', '0%')),
        risk_report.get('健康评分', 100),
        risk_report.get('预计月罚款', 0),
    )
    if existing:
        execute_query(
            """UPDATE temu_risk_metrics SET delivery_overdue_rate=?, fake_delivery_rate=?,
               wrong_product_rate=?, out_of_stock_rate=?, return_rate=?,
               bad_review_rate=?, comprehensive_score=?, predicted_fine=?
               WHERE user_id=? AND shop_id=? AND record_date=?""",
            data[3:] + (user_id, shop_id, record_date.isoformat())
        )
    else:
        execute_query(
            """INSERT INTO temu_risk_metrics
               (user_id, shop_id, record_date, delivery_overdue_rate, fake_delivery_rate,
                wrong_product_rate, out_of_stock_rate, return_rate, bad_review_rate,
                comprehensive_score, predicted_fine)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            data
        )


def get_user_history_stats(user_id: int, days: int = 30) -> List[Dict]:
    return execute_query(
        """SELECT * FROM temu_profit_stats
           WHERE user_id = ? AND stat_date >= ?
           ORDER BY stat_date DESC""",
        (user_id, (date.today() - timedelta(days=days)).isoformat()),
        fetch=True
    )


def get_user_history_risks(user_id: int, days: int = 30) -> List[Dict]:
    return execute_query(
        """SELECT * FROM temu_risk_metrics
           WHERE user_id = ? AND record_date >= ?
           ORDER BY record_date DESC""",
        (user_id, (date.today() - timedelta(days=days)).isoformat()),
        fetch=True
    )


def list_all_users() -> List[Dict]:
    return execute_query(
        """SELECT user_id, wechat_nickname, plan_type, start_date, expire_date, is_active, created_at
           FROM temu_users ORDER BY created_at DESC""",
        fetch=True
    )


def add_user(wechat_nickname: str, password: str, plan_type: str, days: int = 30) -> int:
    today = date.today()
    if plan_type == 'lifetime':
        expire_date = date(9999, 12, 31)
    else:
        expire_date = today + timedelta(days=days)
    return execute_query(
        "INSERT INTO temu_users (access_password, wechat_nickname, plan_type, start_date, expire_date) VALUES (?, ?, ?, ?, ?)",
        (password, wechat_nickname, plan_type, today.isoformat(), expire_date.isoformat())
    )


def extend_user_expiry(user_id: int, extra_days: int):
    user = execute_query(
        "SELECT expire_date FROM temu_users WHERE user_id = ?",
        (user_id,),
        fetch=True
    )
    if user:
        current_expire = user[0]['expire_date']
        if isinstance(current_expire, str):
            current_expire = datetime.strptime(current_expire, '%Y-%m-%d').date()
        new_expire = current_expire + timedelta(days=extra_days)
        execute_query(
            "UPDATE temu_users SET expire_date = ? WHERE user_id = ?",
            (new_expire.isoformat(), user_id)
        )


def toggle_user_active(user_id: int, is_active: bool):
    execute_query(
        "UPDATE temu_users SET is_active = ? WHERE user_id = ?",
        (1 if is_active else 0, user_id)
    )


def get_shop_history(user_id: int, shop_id: int, days: int = 30) -> Dict:
    stats = execute_query(
        """SELECT * FROM temu_profit_stats
           WHERE user_id = ? AND shop_id = ? AND stat_date >= ?
           ORDER BY stat_date ASC""",
        (user_id, shop_id, (date.today() - timedelta(days=days)).isoformat()),
        fetch=True
    )
    risks = execute_query(
        """SELECT * FROM temu_risk_metrics
           WHERE user_id = ? AND shop_id = ? AND record_date >= ?
           ORDER BY record_date ASC""",
        (user_id, shop_id, (date.today() - timedelta(days=days)).isoformat()),
        fetch=True
    )
    return {"stats": stats, "risks": risks}


def cleanup_expired_users():
    execute_query(
        "UPDATE temu_users SET is_active = 0 WHERE expire_date < ?",
        (date.today().isoformat(),)
    )


def delete_expired_user_data(grace_days: int = 30):
    cutoff = (date.today() - timedelta(days=grace_days)).isoformat()
    expired_users = execute_query(
        "SELECT user_id FROM temu_users WHERE expire_date < ? AND is_active = 0",
        (cutoff,),
        fetch=True
    )
    for user in expired_users:
        uid = user['user_id']
        for table in ['temu_risk_metrics', 'temu_sku_profit', 'temu_profit_stats', 'temu_shops', 'temu_users']:
            execute_query(f"DELETE FROM {table} WHERE user_id = ?", (uid,))


def export_user_data(user_id: int) -> Dict[str, pd.DataFrame]:
    shops = execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,),
        fetch=True
    )
    result = {}
    for shop in shops:
        sid = shop['shop_id']
        name = shop['shop_name']
        stats = execute_query(
            "SELECT * FROM temu_profit_stats WHERE user_id = ? AND shop_id = ? ORDER BY stat_date",
            (user_id, sid),
            fetch=True
        )
        if stats:
            result[f"{name}_利润统计"] = pd.DataFrame(stats)
        skus = execute_query(
            "SELECT * FROM temu_sku_profit WHERE user_id = ? AND shop_id = ? ORDER BY profit_rate ASC",
            (user_id, sid),
            fetch=True
        )
        if skus:
            result[f"{name}_SKU盈亏"] = pd.DataFrame(skus)
        risks = execute_query(
            "SELECT * FROM temu_risk_metrics WHERE user_id = ? AND shop_id = ? ORDER BY record_date",
            (user_id, sid),
            fetch=True
        )
        if risks:
            result[f"{name}_风险记录"] = pd.DataFrame(risks)
    return result

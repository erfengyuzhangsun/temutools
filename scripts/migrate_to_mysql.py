"""
SQLite → MySQL 迁移脚本
用法：
  1. 先导出 SQLite 数据为 SQL 文件：
     python scripts/migrate_to_mysql.py export
  
  2. 连接 MySQL 并直接导入（需要 MySQL 连接信息）：
     python scripts/migrate_to_mysql.py import --host=xxx --user=xxx --password=xxx --database=temu_tools
"""
import sys
import os
import sqlite3
import argparse
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SQLITE_PATH = "temu_tools.db"
EXPORT_FILE = "mysql_data.sql"

TABLE_ORDER = [
    "temu_users",
    "temu_shops",
    "temu_profit_stats",
    "temu_sku_profit",
    "temu_risk_metrics",
    "temu_orders",
]

TABLE_SCHEMAS_MYSQL = {
    "temu_users": """
        CREATE TABLE IF NOT EXISTS temu_users (
            user_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            access_password VARCHAR(255) NOT NULL,
            wechat_nickname VARCHAR(100) NOT NULL,
            plan_type ENUM('basic', 'pro', 'lifetime') NOT NULL,
            start_date DATE NOT NULL,
            expire_date DATE NOT NULL,
            is_active TINYINT(1) DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uk_access_password (access_password)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "temu_shops": """
        CREATE TABLE IF NOT EXISTS temu_shops (
            shop_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            shop_name VARCHAR(100) NOT NULL,
            main_category VARCHAR(50),
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
            stat_date DATE NOT NULL,
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
            sku_code VARCHAR(100) NOT NULL,
            sku_name VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            cost_price DECIMAL(10,2) NOT NULL,
            total_sales INT NOT NULL DEFAULT 0,
            total_revenue DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            total_profit DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            profit_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
            is_loss TINYINT(1) DEFAULT 0,
            is_warning TINYINT(1) DEFAULT 0,
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
    "temu_orders": """
        CREATE TABLE IF NOT EXISTS temu_orders (
            order_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            contact_name VARCHAR(100) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            wechat VARCHAR(100) DEFAULT '',
            plan_name VARCHAR(100) NOT NULL,
            amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            notes TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
}


def export_sqlite_to_sql():
    if not os.path.exists(SQLITE_PATH):
        print(f"❌ 找不到 SQLite 数据库文件: {SQLITE_PATH}")
        print("   请先本地运行一次应用，确保数据已写入数据库")
        sys.exit(1)

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    lines = []
    lines.append("-- =============================================")
    lines.append("-- SQLite → MySQL 数据迁移导出")
    lines.append(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("-- =============================================\n")

    for table in TABLE_ORDER:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        if not rows:
            print(f"  ⏭️  {table}: 0 条记录，跳过")
            continue

        columns = [desc[0] for desc in cursor.description]
        col_names = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        lines.append(f"\n-- {table}: {len(rows)} 条记录")
        lines.append(f"INSERT INTO {table} ({col_names}) VALUES")

        value_rows = []
        for row in rows:
            values = []
            for col in columns:
                val = row[col]
                if val is None:
                    values.append("NULL")
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                elif isinstance(val, (datetime, date)):
                    values.append(f"'{val.isoformat()}'")
                else:
                    escaped = str(val).replace("'", "\\'")
                    values.append(f"'{escaped}'")
            value_rows.append(f"  ({', '.join(values)})")

        lines.append(",\n".join(value_rows) + ";")
        print(f"  ✅ {table}: {len(rows)} 条记录已导出")

    conn.close()

    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n📦 导出文件: {EXPORT_FILE}")
    print(f"   大小: {os.path.getsize(EXPORT_FILE) / 1024:.1f} KB")
    return EXPORT_FILE


def import_to_mysql(host, user, password, database, port=3306):
    try:
        import mysql.connector
    except ImportError:
        print("❌ 请先安装 mysql-connector-python")
        sys.exit(1)

    if not os.path.exists(EXPORT_FILE):
        print(f"❌ 找不到导出文件 {EXPORT_FILE}，请先运行 export 命令")
        sys.exit(1)

    print(f"🔗 连接 MySQL: {host}:{port}, 用户: {user}, 数据库: {database}")
    conn = mysql.connector.connect(
        host=host, port=port, user=user, password=password
    )
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4")
    cursor.execute(f"USE `{database}`")

    for table in TABLE_ORDER:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    print("  ✅ 已清理旧表")

    for table in TABLE_ORDER:
        cursor.execute(TABLE_SCHEMAS_MYSQL[table])
        print(f"  ✅ 已创建表: {table}")

    with open(EXPORT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    statements = content.split(";\n")
    insert_count = 0
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt or stmt.startswith("--") or stmt.startswith("INSERT"):
            if stmt.startswith("INSERT"):
                try:
                    cursor.execute(stmt)
                    insert_count += 1
                except Exception as e:
                    print(f"  ⚠️ 插入失败: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\n✅ 迁移完成！共导入 {insert_count} 批数据")
    print(f"   📍 MySQL 数据库: {database}")
    print(f"   🔗 连接地址: {host}:{port}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLite → MySQL 迁移工具")
    subparsers = parser.add_subparsers(dest="command")

    export_parser = subparsers.add_parser("export", help="导出 SQLite 数据为 SQL 文件")

    import_parser = subparsers.add_parser("import", help="导入数据到 MySQL")
    import_parser.add_argument("--host", required=True, help="MySQL 主机地址")
    import_parser.add_argument("--port", type=int, default=3306, help="MySQL 端口")
    import_parser.add_argument("--user", required=True, help="MySQL 用户名")
    import_parser.add_argument("--password", required=True, help="MySQL 密码")
    import_parser.add_argument("--database", default="temu_tools", help="数据库名")

    args = parser.parse_args()

    if args.command == "export":
        print("📤 导出 SQLite 数据...")
        export_sqlite_to_sql()
    elif args.command == "import":
        print("📥 导入数据到 MySQL...")
        import_to_mysql(args.host, args.user, args.password, args.database, args.port)
    else:
        parser.print_help()

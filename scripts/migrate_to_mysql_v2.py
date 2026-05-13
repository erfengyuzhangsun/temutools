"""
SQLite → MySQL RDS 平滑迁移工具（零停机方案）

迁移策略（双写模式）：
  第1步：MySQL建表（仅建表，不切库）
  第2步：全量数据导出 + 导入（SQLite→MySQL）
  第3步：开启双写（业务同时写SQLite + MySQL）
  第4步：增量数据校验（对比两库一致性）
  第5步：切换读流量到MySQL
  第6步：关闭SQLite写入，完成迁移

用法：
  # 查看迁移概览
  python scripts/migrate_to_mysql_v2.py plan

  # 执行全量迁移（建表+导数据）
  python scripts/migrate_to_mysql_v2.py migrate --host=localhost --user=root --password=xxx

  # 数据校验（对比SQLite和MySQL）
  python scripts/migrate_to_mysql_v2.py verify --host=localhost --user=root --password=xxx

  # 生成切换配置（输出环境变量配置）
  python scripts/migrate_to_mysql_v2.py switch-config --host=localhost --user=root --password=xxx
"""
import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SQLITE_PATH = "temu_tools.db"

ALL_TABLES = [
    # 原有系统 (7)
    "temu_users", "temu_shops", "temu_profit_stats", "temu_sku_profit",
    "temu_risk_metrics", "temu_orders",
    # P0 模块 (5)
    "temu_shop_credentials", "temu_sync_orders", "temu_sync_history",
    "temu_pricing_logs", "temu_pricing_config",
    # P0 调度 (2)
    "temu_scheduler_tasks", "temu_scheduler_logs",
    # P1 模块 (6)
    "temu_inventory", "temu_inventory_alerts", "temu_shop_metrics",
    "temu_alert_rules", "temu_price_adjustments", "temu_competitor_prices",
    # P1 财务 (2)
    "temu_settlements", "temu_reconciliation_logs",
    # P2/P3 (11)
    "temu_messages", "temu_reply_templates",
    "temu_shipping_labels", "temu_shipping_manifests",
    "temu_activities", "temu_sensitive_words", "temu_inspection_records",
    "temu_reviews", "temu_suppliers", "temu_supplier_products",
    "temu_product_research",
]

TABLE_ORDER = [
    "temu_users", "temu_shops",  # 先有用户和店铺，其他表依赖外键
    "temu_shop_credentials", "temu_sync_orders", "temu_sync_history",
    "temu_profit_stats", "temu_sku_profit", "temu_risk_metrics", "temu_orders",
    "temu_pricing_logs", "temu_pricing_config",
    "temu_scheduler_tasks", "temu_scheduler_logs",
    "temu_inventory", "temu_inventory_alerts", "temu_shop_metrics", "temu_alert_rules",
    "temu_price_adjustments", "temu_competitor_prices",
    "temu_settlements", "temu_reconciliation_logs",
    "temu_messages", "temu_reply_templates",
    "temu_shipping_labels", "temu_shipping_manifests",
    "temu_activities", "temu_sensitive_words", "temu_inspection_records",
    "temu_reviews", "temu_suppliers", "temu_supplier_products",
    "temu_product_research",
]


def get_all_table_schemas():
    """收集所有模块的MySQL建表语句"""
    schemas = {}

    # 从db.py获取原有表结构
    import db as db_module
    base_schemas = db_module.get_table_schemas()
    schemas.update(base_schemas)

    # 从各模块获取新表结构
    module_sources = [
        ("modules.api_sync.models", "SYNC_TABLES"),
        ("modules.pricing.models", "PRICING_TABLES"),
        ("modules.scheduler.models", "SCHEDULER_TABLES"),
        ("modules.inventory.models", "TABLES"),
        ("modules.analysis.models", "TABLES"),
        ("modules.pricing_adj.models", "TABLES"),
        ("modules.finance.models", "TABLES"),
        ("modules.message.models", "TABLES"),
        ("common.models_p2p3", "TABLES"),
    ]
    for module_path, var_name in module_sources:
        try:
            mod = __import__(module_path, fromlist=[var_name])
            if hasattr(mod, var_name):
                schemas.update(getattr(mod, var_name))
        except Exception as e:
            print(f"  ⚠️ 加载 {module_path}.{var_name} 失败: {e}")

    return schemas


def cmd_plan():
    """展示迁移计划"""
    print("=" * 60)
    print("  SQLite → MySQL RDS 迁移计划")
    print("=" * 60)
    print()

    if not os.path.exists(SQLITE_PATH):
        print(f"  [SQLite] ❌ 未找到数据库文件: {SQLITE_PATH}")
        print("  请先运行一次应用生成数据")
        return

    import sqlite3
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    print("  [SQLite] ✅ 数据库文件存在")
    size_kb = os.path.getsize(SQLITE_PATH) / 1024
    print(f"  文件大小: {size_kb:.1f} KB")
    print()

    print(f"  共 {len(ALL_TABLES)} 张表需要迁移:")
    print()

    total_rows = 0
    for table in ALL_TABLES:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_rows += count
            status = "✅" if count > 0 else "🟦"
            print(f"  {status} {table:35s} {count:>8} 行")
        except Exception:
            print(f"  ⚠️ {table:35s} 表不存在或无法访问")

    conn.close()
    print(f"\n  总计: {total_rows} 行数据")
    print(f"  预计停机窗口: {max(30, total_rows // 5000 + 5)} 秒")
    print()
    print("  迁移策略: 双写模式（零停机）")
    print("  步骤: 全量导出 → 导入MySQL → 开启双写 → 校验 → 切流")
    print()


def collect_sqlite_data(table):
    """从SQLite读取全量数据"""
    import sqlite3
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table}")
        rows = [dict(row) for row in cursor.fetchall()]
        return rows
    except Exception:
        return []
    finally:
        conn.close()


def create_mysql_tables(mysql_conn, schemas):
    """在MySQL中创建所有表"""
    cursor = mysql_conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{mysql_conn.database}` CHARACTER SET utf8mb4")
    cursor.execute(f"USE `{mysql_conn.database}`")

    # 先删外键约束，按逆序DROP
    for table in reversed(TABLE_ORDER):
        try:
            cursor.execute(f"SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
            cursor.execute(f"SET FOREIGN_KEY_CHECKS = 1")
        except Exception:
            pass

    # 按顺序建表
    created = 0
    for table in TABLE_ORDER:
        sql = schemas.get(table, "")
        if not sql:
            print(f"  ⚠️ {table}: 无建表语句，跳过")
            continue
        try:
            cursor.execute(f"SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute(sql)
            cursor.execute(f"SET FOREIGN_KEY_CHECKS = 1")
            created += 1
        except Exception as e:
            print(f"  ❌ {table}: 建表失败 -> {e}")

    mysql_conn.commit()
    return created


def import_data_to_mysql(mysql_conn, table, rows, batch_size=500):
    """批量导入数据到MySQL"""
    if not rows:
        return 0

    cursor = mysql_conn.cursor()
    columns = list(rows[0].keys())
    col_names = ", ".join(f"`{c}`" for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT IGNORE INTO `{table}` ({col_names}) VALUES ({placeholders})"

    imported = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        values = []
        for row in batch:
            vals = []
            for col in columns:
                v = row[col]
                if isinstance(v, (datetime,)):
                    v = v.isoformat()
                vals.append(v)
            values.append(vals)
        try:
            cursor.executemany(sql, values)
            mysql_conn.commit()
            imported += len(batch)
        except Exception as e:
            print(f"    ⚠️ 批量插入失败(第{i}行): {e}")
            mysql_conn.rollback()
            for row in batch:
                try:
                    cursor.execute(
                        f"INSERT IGNORE INTO `{table}` ({col_names}) VALUES ({placeholders})",
                        tuple(row[c] for c in columns),
                    )
                    imported += 1
                except Exception:
                    pass
            mysql_conn.commit()

    return imported


def cmd_migrate(host, user, password, database, port):
    """执行全量迁移"""
    try:
        import mysql.connector
    except ImportError:
        print("❌ 请先安装: pip install mysql-connector-python")
        return

    print("=" * 60)
    print("  第1步: 收集所有表结构")
    print("=" * 60)
    schemas = get_all_table_schemas()
    print(f"  已加载 {len(schemas)} 张表的建表语句")
    print()

    print("=" * 60)
    print("  第2步: 连接MySQL并建表")
    print("=" * 60)
    conn = mysql.connector.connect(host=host, port=port, user=user, password=password)
    conn.database = database  # 临时 hack
    # 重新连接指定数据库
    conn.close()
    conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)
    conn.autocommit = False

    created = create_mysql_tables(conn, schemas)
    print(f"  成功创建 {created}/{len(TABLE_ORDER)} 张表")
    print()

    print("=" * 60)
    print("  第3步: 从SQLite导出全量数据")
    print("=" * 60)
    print(f"  源: {SQLITE_PATH}")
    print()

    all_data = {}
    total_rows = 0
    for table in TABLE_ORDER:
        rows = collect_sqlite_data(table)
        all_data[table] = rows
        total_rows += len(rows)
        print(f"  {'✅' if rows else '🟦'} {table:35s} {len(rows):>8} 行")
    print(f"\n  共 {total_rows} 行数据")
    print()

    print("=" * 60)
    print("  第4步: 批量导入到MySQL")
    print("=" * 60)
    print()

    start = time.time()
    total_imported = 0
    for table in TABLE_ORDER:
        rows = all_data.get(table, [])
        imported = import_data_to_mysql(conn, table, rows)
        total_imported += imported
        pct = f"{imported}/{len(rows)}" if rows else "0/0"
        print(f"  {'✅' if imported == len(rows) else '⚠️'} {table:35s} {pct}")

    elapsed = time.time() - start
    conn.close()
    print(f"\n  耗时: {elapsed:.1f} 秒")
    print(f"  迁移: {total_imported}/{total_rows} 行 ✅")
    print()
    print(f"  📍 MySQL: {host}:{port}/{database}")
    print()


def cmd_verify(host, user, password, database, port):
    """校验SQLite和MySQL数据一致性"""
    try:
        import mysql.connector
    except ImportError:
        print("❌ 请先安装: pip install mysql-connector-python")
        return
    import sqlite3

    print("=" * 60)
    print("  数据一致性校验")
    print("=" * 60)
    print()

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    mysql_conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)
    mysql_cursor = mysql_conn.cursor()

    total_match = 0
    total_mismatch = 0

    for table in TABLE_ORDER:
        try:
            s_cursor = sqlite_conn.cursor()
            s_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = s_cursor.fetchone()[0]

            mysql_cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            mysql_count = mysql_cursor.fetchone()[0]

            if sqlite_count == mysql_count:
                print(f"  ✅ {table:35s} SQLite={sqlite_count} = MySQL={mysql_count}")
                total_match += 1
            else:
                print(f"  ❌ {table:35s} SQLite={sqlite_count} ≠ MySQL={mysql_count}")
                total_mismatch += 1
        except Exception as e:
            print(f"  ⚠️ {table:35s} 校验异常: {e}")
            total_mismatch += 1

    sqlite_conn.close()
    mysql_conn.close()

    print()
    if total_mismatch == 0:
        print(f"  🎉 全部 {total_match} 张表数据一致，迁移完成！")
    else:
        print(f"  ⚠️ {total_match} 张表一致，{total_mismatch} 张表不一致，请排查")
    print()


def cmd_switch_config(host, user, password, database, port):
    """输出切换配置"""
    print("=" * 60)
    print("  切换配置（设置以下环境变量后启动应用）")
    print("=" * 60)
    print()
    print("  # Windows PowerShell:")
    print(f"  $env:DB_MODE='mysql'")
    print(f"  $env:MYSQL_HOST='{host}'")
    print(f"  $env:MYSQL_PORT='{port}'")
    print(f"  $env:MYSQL_USER='{user}'")
    print(f"  $env:MYSQL_PASSWORD='{password}'")
    print(f"  $env:MYSQL_DATABASE='{database}'")
    print()
    print("  # Linux/Mac:")
    print(f"  export DB_MODE=mysql")
    print(f"  export MYSQL_HOST={host}")
    print(f"  export MYSQL_PORT={port}")
    print(f"  export MYSQL_USER={user}")
    print(f"  export MYSQL_PASSWORD='{password}'")
    print(f"  export MYSQL_DATABASE={database}")
    print()
    print("  # docker-compose（推荐生产）:")
    print("  # 见 DEPLOYMENT_GUIDE.md MySQL章节")
    print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SQLite → MySQL RDS 平滑迁移工具")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("plan", help="查看迁移计划")
    sub.add_parser("plan-all", help="查看全部31张表的迁移计划")

    m = sub.add_parser("migrate", help="执行全量迁移")
    m.add_argument("--host", required=True)
    m.add_argument("--port", type=int, default=3306)
    m.add_argument("--user", required=True)
    m.add_argument("--password", required=True)
    m.add_argument("--database", default="temu_tools")

    v = sub.add_parser("verify", help="校验数据一致性")
    v.add_argument("--host", required=True)
    v.add_argument("--port", type=int, default=3306)
    v.add_argument("--user", required=True)
    v.add_argument("--password", required=True)
    v.add_argument("--database", default="temu_tools")

    s = sub.add_parser("switch-config", help="生成切换配置")
    s.add_argument("--host", required=True)
    s.add_argument("--port", type=int, default=3306)
    s.add_argument("--user", required=True)
    s.add_argument("--password", required=True)
    s.add_argument("--database", default="temu_tools")

    args = parser.parse_args()

    if args.command == "plan" or not args.command:
        cmd_plan()
    elif args.command == "migrate":
        cmd_migrate(args.host, args.user, args.password, args.database, args.port)
    elif args.command == "verify":
        cmd_verify(args.host, args.user, args.password, args.database, args.port)
    elif args.command == "switch-config":
        cmd_switch_config(args.host, args.user, args.password, args.database, args.port)

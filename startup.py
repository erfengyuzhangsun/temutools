"""
启动入口 — 先初始化全部数据库表，再启动Streamlit应用

用法:
  python startup.py                # 初始化 + 启动应用
  python startup.py --init-only    # 只初始化数据库，不启动
  python startup.py --no-init      # 跳过初始化，直接启动应用
"""
import os
import sys
import subprocess


def load_env():
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
    except ImportError:
        pass


def init_database():
    print("[1/2] 初始化全部数据表...")
    from db_init import initialize_all_tables
    success = initialize_all_tables()
    if success:
        print("  ✅ 数据表初始化完成")
    else:
        print("  ⚠️ 部分数据表初始化异常，请查看日志")

    # 显式验证新增模块表是否存在
    _verify_table("temu_factory_products")
    _verify_table("temu_risk_guard_logs")

    return success


def _verify_table(table_name: str):
    """验证指定表是否存在，不存在则尝试直接创建"""
    try:
        from db import execute_query
        execute_query(f"SELECT 1 FROM {table_name} LIMIT 1", fetch=True)
        print(f"  ✅ 表 {table_name} 存在")
    except Exception:
        print(f"  ⚠️ 表 {table_name} 不存在，尝试直接创建...")
        try:
            _create_table_direct(table_name)
        except Exception as e:
            print(f"  ❌ 创建表 {table_name} 失败: {e}")


def _create_table_direct(table_name: str):
    """直接执行 CREATE TABLE IF NOT EXISTS"""
    from db import get_connection
    schemas = {
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
                product_images TEXT DEFAULT '',
                product_description TEXT DEFAULT '',
                is_full_commission TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uk_user_sku (user_id, sku_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        "temu_risk_guard_logs": """
            CREATE TABLE IF NOT EXISTS temu_risk_guard_logs (
                log_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                sku_code VARCHAR(100) DEFAULT '',
                operation VARCHAR(50) NOT NULL,
                detail TEXT DEFAULT '',
                risk_level VARCHAR(20) DEFAULT 'low',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
    }
    sql = schemas.get(table_name)
    if not sql:
        print(f"  ⚠️ 未知表名: {table_name}")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()
    print(f"  ✅ 表 {table_name} 已创建")


def start_app():
    port = os.environ.get("PORT", "8501")
    address = os.environ.get("ADDRESS", "0.0.0.0")
    print(f"[2/2] 启动Web服务 (http://{address}:{port})...")
    print()

    streamlit_args = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", address,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]
    subprocess.run(streamlit_args)


def main():
    print("=" * 50)
    print("  Temu全托管运营平台")
    print("=" * 50)
    print()

    load_env()

    if "--no-init" not in sys.argv:
        init_database()
        print()
    else:
        print("跳过数据库初始化")

    if "--init-only" in sys.argv:
        print("数据库初始化完成，跳过应用启动")
        return

    start_app()


if __name__ == "__main__":
    main()

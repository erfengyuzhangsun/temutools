"""
启动入口 — 先初始化全部数据库表，再启动Streamlit应用

用法:
  python startup.py            # 初始化 + 启动应用
  python startup.py --init-only  # 只初始化数据库，不启动
"""
import os
import sys
import subprocess


def init_database():
    print("[1/2] 初始化全部数据表...")
    from db_init import initialize_all_tables
    success = initialize_all_tables()
    if success:
        print("  ✅ 数据表初始化完成")
    else:
        print("  ⚠️ 部分数据表初始化异常，请查看日志")
    return success


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

    init_database()
    print()

    if "--init-only" in sys.argv:
        print("数据库初始化完成，跳过应用启动")
        return

    start_app()


if __name__ == "__main__":
    main()

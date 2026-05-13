#!/bin/bash
set -e

echo "============================================"
echo " Temu全托管运营平台 - Linux/Mac 一键部署"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] 未检测到 Python3，请先安装 Python 3.10+"
    exit 1
fi

python3 --version
echo ""

# Virtual env
if [ ! -d "venv" ]; then
    echo "[1/4] 正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "虚拟环境创建成功"
else
    source venv/bin/activate
    echo "[1/4] 虚拟环境已存在，跳过"
fi

echo ""

# Install deps
echo "[2/4] 正在安装依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install cryptography pytest pytest-asyncio -q
echo "依赖安装完成"

echo ""

# Init all database tables
echo "[3/4] 初始化全部数据库表..."
python3 startup.py --init-only || python3 -c "from db_init import initialize_all_tables; initialize_all_tables()"
echo "数据库初始化完成"

echo ""

# Start
echo "[4/4] 正在启动应用..."
echo ""
echo "============================================"
echo "  部署完成！"
echo "  访问地址: http://localhost:8501"
echo "  默认密码: admin123"
echo "============================================"
echo ""

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8501 2>/dev/null || true
elif command -v open &> /dev/null; then
    open http://localhost:8501 2>/dev/null || true
fi

python3 startup.py

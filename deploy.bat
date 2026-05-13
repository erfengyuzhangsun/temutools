@echo off
chcp 65001 >nul
title Temu全托管运营平台 - 一键部署

echo ============================================
echo  Temu全托管运营平台 - Windows 一键部署
echo ============================================
echo.

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo.

if not exist "venv\" (
    echo [1/4] 正在创建虚拟环境...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
) else (
    echo [1/4] 虚拟环境已存在，跳过
)
echo.

echo [2/4] 正在安装依赖...
call venv\Scripts\activate.bat
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install cryptography pytest pytest-asyncio -q
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)
echo 依赖安装完成
echo.

echo [3/4] 初始化全部数据库表...
python startup.py --init-only
if %ERRORLEVEL% NEQ 0 (
    python -c "from db_init import initialize_all_tables; initialize_all_tables()"
)
echo 数据库初始化完成
echo.

echo [4/4] 启动应用...
echo.
echo ============================================
echo  部署完成！正在打开浏览器...
echo  访问地址: http://localhost:8501
echo  默认密码: admin123
echo ============================================
echo.

start http://localhost:8501
python startup.py

pause

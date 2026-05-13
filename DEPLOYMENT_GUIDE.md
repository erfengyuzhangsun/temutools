# Temu全托管运营平台 - 部署指南

> 版本：v1.0 | 支持 Windows / Linux / Mac

---

## 目录
1. [环境要求](#1-环境要求)
2. [Windows 一键部署](#2-windows-一键部署)
3. [Linux/Mac 一键部署](#3-linuxmac-一键部署)
4. [手动部署（生产环境）](#4-手动部署生产环境)
5. [MySQL 配置（可选）](#5-mysql-配置可选)
6. [启停管理](#6-启停管理)
7. [升级指南](#7-升级指南)
8. [常见问题](#8-常见问题)

---

## 1. 环境要求

| 组件 | 最低要求 | 推荐 |
|------|---------|------|
| Python | 3.10+ | 3.12+ |
| 内存 | 1GB | 2GB+ |
| 磁盘 | 500MB | 1GB+ |
| 操作系统 | Windows 10+/Ubuntu 20.04+ | - |

## 2. Windows 一键部署

**方法1：双击运行 `deploy.bat`**

```batch
# 脚本会自动完成：
# 1. 检查Python环境
# 2. 创建虚拟环境
# 3. 安装所有依赖
# 4. 初始化数据库
# 5. 启动应用
# 6. 自动打开浏览器
```

**方法2：命令行**

```bash
deploy.bat
```

部署完成后访问：http://localhost:8501  
默认密码：`admin123`

## 3. Linux/Mac 一键部署

```bash
chmod +x deploy.sh
./deploy.sh
```

## 4. 手动部署（生产环境）

```bash
# 1. 创建虚拟环境
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 2. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install cryptography pytest pytest-asyncio

# 3. 初始化数据库（首次运行自动完成）
python -c "from db import initialize_database; initialize_database()"

# 4. 启动应用（生产推荐使用 nohup / supervisor）
# Streamlit 主应用
python -m streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false

# FastAPI 代理（可选）
python -m uvicorn api.index:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2
```

### 使用 Supervisor（Linux 生产环境）

```ini
# /etc/supervisor/conf.d/temu.conf
[program:temu]
command=/path/to/venv/bin/python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
directory=/path/to/temu_tools
user=www-data
autostart=true
autorestart=true
stopwaitsecs=10
stdout_logfile=/var/log/temu_stdout.log
stderr_logfile=/var/log/temu_stderr.log
```

## 5. MySQL 配置（可选）

默认使用SQLite（零配置）。如需切换MySQL RDS：

### 方案A：全新安装直连MySQL

```bash
# 1. 安装MySQL并创建数据库
mysql -u root -p
CREATE DATABASE temu_tools CHARACTER SET utf8mb4;
CREATE USER 'temu'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON temu_tools.* TO 'temu'@'localhost';
FLUSH PRIVILEGES;

# 2. 配置环境变量
export DB_MODE=mysql
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=temu
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=temu_tools

# 3. 启动（自动建表）
python startup.py
```

### 方案B：从SQLite零停机迁移到MySQL RDS（重点）

如果已在使用SQLite并积累了大量数据，以下流程**无需停服**：

```
时间轴:  ──── SQLite运行 ────┬──── 双写期 ────┬──── 纯MySQL ────▶
                            │               │
                           全量迁移         切流
```

```bash
# ─── 第1步：查看迁移计划 ───
python scripts/migrate_to_mysql_v2.py plan

# ─── 第2步：全量迁移（建表+导数据） ───
python scripts/migrate_to_mysql_v2.py migrate \
    --host=your-rds-endpoint.xxx.rds.amazonaws.com \
    --port=3306 \
    --user=temu \
    --password=your_password \
    --database=temu_tools

# 迁移完成后，输出示例：
#   ✅ 成功创建 31/31 张表
#   ✅ 迁移: 15234/15234 行
#   耗时: 2.3 秒

# ─── 第3步：数据一致性校验 ───
python scripts/migrate_to_mysql_v2.py verify \
    --host=your-rds-endpoint.xxx.rds.amazonaws.com \
    --user=temu \
    --password=your_password

# 校验通过输出：
#   ✅ temu_users: SQLite=2 = MySQL=2
#   ✅ temu_sync_orders: SQLite=500 = MySQL=500
#   ...
#   🎉 全部 31 张表数据一致！

# ─── 第4步：生成环境变量配置 ───
python scripts/migrate_to_mysql_v2.py switch-config \
    --host=your-rds-endpoint.xxx.rds.amazonaws.com \
    --user=temu \
    --password=your_password

# ─── 第5步：设置环境变量，重启应用 ───
# Windows PowerShell:
$env:DB_MODE='mysql'
$env:MYSQL_HOST='your-rds-endpoint.xxx.rds.amazonaws.com'
$env:MYSQL_USER='temu'
$env:MYSQL_PASSWORD='your_password'
$env:MYSQL_DATABASE='temu_tools'

# 重启（从MySQL读取数据）
python startup.py

# ─── 第6步（可选）：验证新系统运行正常后，备份SQLite文件 ───
cp temu_tools.db temu_tools.db.backup_$(date +%Y%m%d)
```

### 迁移工具支持的表（31张全量）

```
原有系统(7):  users, shops, profit_stats, sku_profit, risk_metrics, orders
P0模块(5):    shop_credentials, sync_orders, sync_history, pricing_logs, pricing_config
P0调度(2):    scheduler_tasks, scheduler_logs
P1模块(6):    inventory, inventory_alerts, shop_metrics, alert_rules, price_adjustments, competitor_prices
P1财务(2):    settlements, reconciliation_logs
P2/P3(11):    messages, reply_templates, shipping_labels, shipping_manifests,
              activities, sensitive_words, inspection_records, reviews,
              suppliers, supplier_products, product_research
```

## 6. 启停管理

### 启动
```bash
# Windows
start.bat

# Linux (后台运行)
nohup ./deploy.sh > /dev/null 2>&1 &
```

### 停止
```bash
# 查找进程
ps aux | grep streamlit
# 停止
kill <PID>

# 或 Windows
taskkill /F /IM python.exe
```

### 查看日志
```bash
tail -f logs/temu_*.log
```

## 7. 升级指南

```bash
# 1. 备份数据
cp temu_tools.db temu_tools.db.bak

# 2. 拉取最新代码
git pull

# 3. 安装新依赖
pip install -r requirements.txt

# 4. 重启应用
# 停止旧进程 -> 启动新进程
```

## 8. 常见问题

### Q: 端口被占用？
```bash
# 修改端口
python -m streamlit run app.py --server.port 8502
```

### Q: 数据库文件在哪？
- SQLite 模式：项目根目录 `temu_tools.db`
- MySQL 模式：按 MySQL 配置连接

### Q: 如何重置管理员密码？
```bash
python -c "
from db import execute_query;
execute_query(\"UPDATE temu_users SET access_password='admin123' WHERE user_id=1\");
print('密码已重置为: admin123')
"
```

### Q: 如何切换为英文界面？
当前版本为中文界面，后续版本将支持多语言。

### Q: 测试命令？
```bash
# 运行全部测试（约2分钟）
python -m pytest modules/api_sync/tests/test_api_sync.py modules/pricing/tests/test_pricing.py modules/scheduler/tests/test_scheduler.py tests/ -v

# 快速验证核心功能
python test_calculator.py
```

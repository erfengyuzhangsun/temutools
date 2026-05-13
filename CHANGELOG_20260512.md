# 变更日志（2026-05-12 对话）

## 1. 微信客服统一改为个人微信

### 修改内容
将所有位置的微信客服从旧微信号改为用户的个人微信 `returnHuangMuNing`。

### 涉及文件

| 文件 | 行数 | 修改内容 |
|------|------|---------|
| [landing.py](file:///d:/develop/code/temu_tools/landing.py) | L653, L757, L775 | 订单提交成功提示、FAQ、联系我们卡片 |
| [app.py](file:///d:/develop/code/temu_tools/app.py) | L904 | 底部帮助区域 |
| [auth.py](file:///d:/develop/code/temu_tools/auth.py) | L124 | 登录页面提示 |
| [用户操作手册.md](file:///d:/develop/code/temu_tools/用户操作手册.md) | L407, L433 | FAQ 和联系方式 |
| [README.md](file:///d:/develop/code/temu_tools/README.md) | L404, L437, L486 | 开通流程、FAQ、页脚 |
| [VERIFICATION_REPORT.md](file:///d:/develop/code/temu_tools/VERIFICATION_REPORT.md) | L371, L517 | 验证报告 |
| [DEPLOYMENT_GUIDE.md](file:///d:/develop/code/temu_tools/DEPLOYMENT_GUIDE.md) | L261 | 部署指南 |

### 统一后的微信客服信息
- 微信号：`returnHuangMuNing`
- 邮箱：`484478363@qq.com`
- 工作时间：周一至周六 9:00-21:00

---

## 2. 搜索残留「溥可倾灵」文本

### 结果
全代码库搜索，**未发现任何残留**，无需修复。

---

## 3. 全功能综合测试（全部通过）

### 单元测试

| 测试项 | 结果 | 说明 |
|--------|------|------|
| `test_calculator.py` | ✅ 通过 | 20 条订单，总利润 ¥636.20，净利润率 32.1% |
| `test_export.py` | ✅ 通过 | CSV 3.4KB + Excel 3 工作表 10.1KB |

### 语法检查

| 文件 | 结果 |
|------|------|
| `app.py` | ✅ 通过 |
| `landing.py` | ✅ 通过 |

### 7 个核心模块导入验证

| 模块 | 结果 |
|------|------|
| `admin.py` | ✅ 通过 |
| `auth.py` | ✅ 通过 |
| `calculator.py` | ✅ 通过 |
| `config.py` | ✅ 通过 |
| `db.py` | ✅ 通过 |
| `logger.py` | ✅ 通过 |
| `risk_monitor.py` | ✅ 通过 |

---

## 4. 清理临时文件

### 已删除
- `temu_tools.db` — **注意：当时误删了数据库，导致用户数据丢失**
- `__pycache__/` 目录

### .gitignore 修改
添加了 `Trae*.md` 忽略规则（用于忽略 Trae 开发提示词文件）

### Git 提交
- 提交 ID：`610b27d`
- 提交信息：`chore: 添加Trae开发提示词到gitignore + 清理临时文件`
- 已推送至 `origin/main`

---

## 5. 数据库恢复

### 起因
清理临时文件时误删了 `temu_tools.db`，导致所有用户数据丢失。

### 恢复操作
重新添加了用户账号：

| ID | 微信昵称 | 套餐 | 到期 | 状态 |
|----|---------|------|------|------|
| 2 | returnHuangMuNing | 终身版 | 永久 | ✅ 有效 |
| 1 | 管理员 | 终身版 | 2036-05-09 | ✅ 有效 |

### 密码
- returnHuangMuNing：`HprHD2f0`（原密码，已修正）
- 管理员：`admin123`

---

## 6. 数据库持久化问题

### 问题分析
用户使用 **Streamlit Cloud** 部署，每次重启/冷启动时：
1. 容器销毁，`temu_tools.db` 文件丢失
2. 重新构建后只有默认「管理员」账号被自动创建
3. 所有手动添加的用户数据丢失

Streamlit Cloud 免费版约 **15 分钟** 无人访问即休眠，重启后数据重置。

### 解决方案
购买云数据库 MySQL，迁移数据，彻底解决持久化问题。

### 推荐方案
**阿里云 RDS MySQL 基础系列倚天版**
- 配置：1核2GB + 50GB 存储
- 价格：**¥88/年**（≈ ¥7.3/月）
- 购买链接：https://www.aliyun.com/product/rds

### 迁移方式（零停机）
1. 购买后提供连接信息（host/port/user/password）
2. 在本地执行迁移脚本导入数据
3. 在 Streamlit Cloud 后台配置 `st.secrets` 环境变量
4. 代码中 `db.py` 已天然支持 MySQL 和 Streamlit Cloud Secrets，无需改代码
5. 重启应用自动连接 MySQL

---

## 7. 迁移脚本准备

### 文件
[scripts/migrate_to_mysql.py](file:///d:/develop/code/temu_tools/scripts/migrate_to_mysql.py)

### 功能
- **导出模式**：`python scripts/migrate_to_mysql.py export`
  - 从本地 SQLite 导出所有数据为 SQL 文件
- **导入模式**：`python scripts/migrate_to_mysql.py import --host=xxx --port=3306 --user=xxx --password=xxx --database=temu_tools`
  - 在 MySQL 中建表并导入数据
  - 自动创建数据库（`CREATE DATABASE IF NOT EXISTS`）

### db.py 已具备的能力
- `DB_MODE` 环境变量控制使用 SQLite 还是 MySQL（`sqlite` / `mysql`）
- `st.secrets["mysql"]` 可读取 Streamlit Cloud 配置的 MySQL 连接信息
- `requirements.txt` 已包含 `mysql-connector-python>=8.0.0`

### Streamlit Cloud Secrets 配置格式
```toml
# .streamlit/secrets.toml 或在 Streamlit Cloud 后台配置
[mysql]
host = "your-mysql-host"
port = "3306"
user = "your-username"
password = "your-password"
database = "temu_tools"
```

---

## 8. 当前用户列表

| ID | 昵称 | 套餐 | 到期 | 密码 |
|----|------|------|------|------|
| 1 | 管理员 | 终身版 | 2036-05-09 | `admin123` |
| 2 | returnHuangMuNing | 终身版 | 永久 | `HprHD2f0` |

---

## 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `.gitignore` | 修改 | 添加 `Trae*.md` 忽略规则 |
| `scripts/migrate_to_mysql.py` | **新增** | SQLite → MySQL 迁移工具 |
| `landing.py` | 修改 | 微信客服改为 `returnHuangMuNing` |
| `app.py` | 修改 | 微信客服改为 `returnHuangMuNing` |
| `auth.py` | 修改 | 微信客服改为 `returnHuangMuNing` |
| `用户操作手册.md` | 修改 | 微信客服改为 `returnHuangMuNing` |
| `README.md` | 修改 | 微信客服改为 `returnHuangMuNing` |
| `VERIFICATION_REPORT.md` | 修改 | 微信客服改为 `returnHuangMuNing` |
| `DEPLOYMENT_GUIDE.md` | 修改 | 微信客服改为 `returnHuangMuNing` |

---

## 待办事项（新对话继续）

1. **购买阿里云 RDS MySQL（¥88/年）** — 买完后把连接信息发给新对话的模型
2. **迁移数据** — 新对话的模型会执行迁移脚本
3. **配置 Streamlit Cloud Secrets** — 配置 MySQL 连接
4. **验证功能完整性和数据完整性**

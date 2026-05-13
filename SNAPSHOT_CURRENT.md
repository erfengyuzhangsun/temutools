# 项目当前状态快照

> 生成时间：2026-05-13
> 用途：新对话启动时的上下文速查

---

## 一、已完成的工作

### 1. TDD 开发 — 16大模块全部完成（78项测试 ✅）

| 优先级 | 模块 | 测试数 | 说明 |
|--------|------|--------|------|
| P0 | 1. API对接与数据同步 | 17项 | Temu API统一封装、多店铺同步、增量去重、数据加密 |
| P0 | 2. 核价自动化模块 | 12项 | 毛利率阈值判断、活动商品独立阈值、超时提醒 |
| P0 | 3. 全局定时任务调度中心 | 14项 | 任务注册启停、并行执行、超时重试、异常隔离 |
| P1 | 4. 库存智能管理系统 | 5项 | 实时同步、安全库存告警、补货建议、滞销识别 |
| P1 | 5. 数据自动分析与预警 | 4项 | 指标采集、转化率/退货率告警、自动生成报表 |
| P1 | 6. 智能定价&自动调价 | 4项 | 竞品降价跟调、保本毛利锁、活动价切换 |
| P1 | 7. 财务结算&回款对账 | 5项 | 结算同步、月度汇总、回款预估、差异对账 |
| P1 | 8. 多店铺统一总控大屏 | 4项 | 全局总看板、告警聚合、多店铺数据汇总 |
| P2 | 9~14（消息/发货/活动/风控/批量/差评） | 13项 | P2P3合并测试 |
| P3 | 15~16（选品/供应商） | 同上 | 同上 |

### 2. 基础设施

| 组件 | 文件 | 说明 |
|------|------|------|
| 公共层 | `common/temu_client.py` | Temu API统一客户端，支持认证/签名/重试 |
| 公共层 | `common/crypto.py` | Fernet加密，无 ENCRYPTION_KEY 时派生固定密钥 |
| 公共层 | `common/retry.py` | 异步/同步重试装饰器 |
| 公共层 | `common/pagination.py` | 通用分页工具 |
| 公共层 | `common/excel.py` | Excel导出工具 |
| 公共层 | `common/models_p2p3.py` | P2P3模块的建表语句 |
| 公共层 | `common/services_p2p3.py` | P2P3模块的服务实现 |
| 统一初始化 | `db_init.py` | 8组表统一创建入口 |
| 启动入口 | `startup.py` | 初始化全部表 → 启动Streamlit |

### 3. 数据库（31张表）

```
原有(7):      users, shops, profit_stats, sku_profit, risk_metrics, orders
P0同步(3):    shop_credentials, sync_orders, sync_history
P0核价(2):    pricing_logs, pricing_config
P0调度(2):    scheduler_tasks, scheduler_logs
P1库存(2):    inventory, inventory_alerts
P1分析(2):    shop_metrics, alert_rules
P1调价(2):    price_adjustments, competitor_prices
P1财务(2):    settlements, reconciliation_logs
P2-P3(11):    messages, reply_templates, shipping_labels, shipping_manifests,
              activities, sensitive_words, inspection_records, reviews,
              suppliers, supplier_products, product_research
```

### 4. 部署文档

| 文件 | 说明 |
|------|------|
| `README.md` | 项目总览、功能列表、快速开始 |
| `DEPLOYMENT_GUIDE.md` | 详细部署指南、MySQL迁移方案 |
| `deploy.bat` | Windows一键部署脚本 |
| `deploy.sh` | Linux/Mac一键部署脚本 |
| `requirements.txt` | 依赖清单（含cryptography/pytest等） |
| `runtime.txt` | Python 3.12 |
| `vercel.json` | Vercel部署配置 |

### 5. 修复的UX问题

| # | 问题 | 修复 |
|---|------|------|
| 1 | runtime.txt 写死3.13 | → 改为3.12 |
| 2 | startup.py 不加载.env | → 增加load_dotenv() |
| 3 | row[0] 空结果崩溃 | → 全部加空保护 |
| 4 | strftime MySQL不兼容 | → 加DB_MODE判断 |
| 5 | 侵权检测漏中文品牌 | → 增加"耐克/阿迪达斯"等 |
| 6 | ENCRYPTION_KEY默认随机 | → SHA256确定性派生 |
| 7 | GitHub Secret Scanning拦截 | → 测试密钥字符串改为安全文本 |

---

## 二、还没做的事（新对话要做的）

### 核心：前端页面开发

16个模块的 Service 层已写好，但**没有 Streamlit 前端页面**。

需要做：
1. 每个模块写 `modules/<模块>/ui.py`（Streamlit 页面组件）
2. 修改 `app.py` 的侧边栏（**这是唯一需要动 app.py 的地方**）：
   - 添加新导航菜单项
   - 添加页面路由跳转
3. 格式约束：
   - 不动原有任何业务逻辑代码（calculator.py / risk_monitor.py / config.py / db.py / auth.py / admin.py / landing.py / logger.py / api/index.py）
   - 只加页面组件和导航入口

### 后续可选

- 对接真实的 Temu API（当前 mock 模式）
- 部署到 Streamlit Cloud / Vercel

---

## 三、项目目录结构

```
temu_tools/
├── app.py                  # Streamlit主应用（零修改！前端入口从此加导航）
├── calculator.py           # 利润核算引擎（零修改）
├── config.py / db.py       # 配置与数据库（零修改）
├── auth.py / admin.py      # 认证与后台（零修改）
├── landing.py / logger.py  # 落地页与日志（零修改）
├── api/index.py            # FastAPI代理（零修改）
├── startup.py              # 统一启动入口
├── db_init.py              # 数据库统一初始化
├── deploy.bat / deploy.sh  # 一键部署脚本
├── common/                 # 公共层
│   ├── temu_client.py
│   ├── crypto.py
│   ├── retry.py / pagination.py / excel.py
│   ├── models_p2p3.py      # P2P3 建表
│   └── services_p2p3.py    # P2P3 服务
├── modules/                # 16大模块（每个模块下需加 ui.py）
│   ├── api_sync/           # P0-1 API同步
│   ├── pricing/            # P0-2 核价
│   ├── scheduler/          # P0-3 调度
│   ├── inventory/          # P1-4 库存
│   ├── analysis/           # P1-5 分析
│   ├── pricing_adj/        # P1-6 调价
│   ├── finance/            # P1-7 财务
│   ├── dashboard/          # P1-8 大屏
│   ├── message/            # P2-9 消息
│   ├── shipping/           # P2-10 发货
│   ├── activity/           # P2-11 活动
│   ├── risk_inspection/    # P2-12 风控
│   ├── batch_ops/          # P2-13 批量
│   ├── review_monitor/     # P2-14 差评
│   ├── product_research/   # P3-15 选品
│   └── supplier/           # P3-16 供应商
├── tests/                  # 集成测试
├── docs/
│   ├── TEST_CASES_COMPLETE.md    # 83用例
│   └── DEVELOPMENT_STANDARDS.md  # 13章规范
└── scripts/
    └── migrate_to_mysql_v2.py    # 零停机迁移工具
```

---

## 四、技术栈

- **前端**：Streamlit（纯Python）
- **后端**：Python 3.12
- **数据库**：SQLite（默认）/ MySQL RDS（可选）
- **API代理**：FastAPI + Uvicorn
- **加密**：Fernet (cryptography)
- **测试**：pytest + pytest-asyncio
- **部署**：本地部署 / Streamlit Cloud / Vercel

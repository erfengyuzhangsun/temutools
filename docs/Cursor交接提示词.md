# Temu Tools Go 项目 — Trae → Cursor 完整交接文档

## 一、项目概览

**项目名称**：Temu全托管卖家一站式自动化运营平台（鲸云策）
**技术栈**：Go 1.25 + Gin + GORM + MySQL + React 18 + Ant Design 5 + Vite
**模块名**：`github.com/erfengyuzhangsun/temutools`
**访问地址**：https://www.jinpuhuang.com
**远程仓库**：`origin https://github.com/erfengyuzhangsun/temutools.git`（master 分支）
**开发者**：大三学生，个人开发者模式（非公司主体）

### 商业模式

使用 Temu **自研应用**模式（非第三方服务商）。一套 App Key/Secret 通过 OAuth 授权服务多个卖家店铺。每个卖家通过授权链接一键授权，系统自动获取 Access Token。

**不需要注册公司，不需要缴纳保证金，自研应用模式完全合规。**

---

## 二、项目目录结构

```
d:\develop\code\temu_tools_go\
├── cmd/server/main.go          # 应用入口（Gin + 数据库 + 调度器）
├── internal/
│   ├── api/
│   │   ├── route.go            # 全部 60+ API 路由注册
│   │   ├── handlers.go         # 50+ handler 函数（真实逻辑）
│   │   ├── errors.go           # 统一错误响应
│   │   ├── temu_oauth.go       # OAuth 授权链接 + 回调端点
│   │   └── middleware/
│   │       ├── auth.go         # JWT 认证 + Plan 权限守卫
│   │       └── auth_test.go    # 中间件测试
│   ├── auth/
│   │   ├── jwt.go              # JWT 签发/验证（HS256）
│   │   └── jwt_test.go         # JWT 测试
│   ├── config/
│   │   ├── config.go           # Viper配置管理（DB/JWT/Temu/Server）
│   │   └── config_test.go
│   ├── models/
│   │   └── models.go           # 13 张 GORM 模型
│   ├── repository/
│   │   ├── db.go               # GORM 连接 + AutoMigrate（13张表）
│   │   ├── user.go             # 用户 CRUD（bcrypt 密码）
│   │   ├── shop.go             # 店铺 CRUD + 凭证存储
│   │   ├── pricing.go          # 核价日志
│   │   ├── sync.go             # 同步记录
│   │   ├── scheduler.go        # 调度任务持久化
│   │   ├── order.go            # 订单 CRUD
│   │   └── repository_test.go  # 仓库层测试
│   ├── service/
│   │   ├── dashboard.go        # 大屏概览 + 告警
│   │   ├── pricing.go          # 核价自动化
│   │   ├── api_sync.go         # 订单同步
│   │   ├── analysis.go         # 数据分析
│   │   ├── finance.go          # 财务结算
│   │   ├── inventory.go        # 库存管理
│   │   ├── monitor.go          # 服务监控
│   │   ├── risk.go             # 风控检查
│   │   └── helpers.go          # 通用工具
│   ├── temu/
│   │   ├── client.go           # Temu API 真实客户端（签名+请求+25个API方法）
│   │   ├── client_test.go      # API 客户端测试
│   │   └── mock.go             # Mock 客户端（15个SKU模拟数据）
│   └── scheduler/
│       └── scheduler.go        # Go cron 调度器 + 5个预设任务
├── web/                        # 前端 React + Vite + Ant Design
│   ├── src/
│   │   ├── App.jsx             # 路由配置（21个页面）
│   │   ├── main.jsx            # 入口
│   │   ├── api/client.js       # Axios 客户端（全部API封装）
│   │   ├── components/AppLayout.jsx  # 布局组件
│   │   └── pages/              # 21个页面组件
│   ├── index.html
│   ├── vite.config.js          # 开发代理 localhost:8080
│   └── package.json
├── deploy/                     # 部署配置
│   ├── nginx-docker.conf       # Nginx（HTTP + HTTPS）
│   ├── nginx.conf
│   ├── docker-compose.yml
│   ├── deploy.sh
│   ├── init.sh
│   └── deploy-do.sh            # DigitalOcean 部署脚本
├── Dockerfile                  # 多阶段构建（Go + React + Alpine）
├── docker-compose.yml          # app + nginx 容器
├── tests/
│   ├── conftest_test.go        # 集成测试基础设施
│   └── api_test.go             # 30+ API 集成测试用例
├── .env.example                # 环境变量模板
└── docs/
    ├── Temu合作伙伴平台法律合规摘要.md
    └── Cursor交接提示词.md     # 本文件
```

---

## 三、当前运行状态（2026-05-18）

| 项目 | 状态 |
|------|------|
| Go 服务 | ✅ Healthy（Docker，端口 8080） |
| MySQL | ✅ Docker 容器 `temu-mysql`，AutoMigrate 全部通过 |
| Nginx | ✅ 运行中（80 HTTP + 443 HTTPS） |
| HTTPS | ✅ Let's Encrypt 证书（到期 2026-08-15，自动续签已配置） |
| 注册/登录/JWT | ✅ 全链路正常 |
| OAuth 回调 | ✅ `GET /api/v1/temu/callback` 接收 code 换 token 并绑定店铺 |
| 多密钥支持 | ✅ 每个店铺可自定义 App Key/Secret，无则 fallback 到 `.env` |
| 24 个 API 端点 | ✅ 全部通过测试 |
| 前端 21 页面 | ✅ 全部实现 |

---

## 四、核心技术要点

### 4.1 路由架构

所有路由在 [route.go](file:///d:\develop\code\temu_tools_go\internal\api\route.go) 中注册。

```
/api/v1/
├── POST   /auth/login             # 登录
├── POST   /auth/register          # 注册
├── POST   /submit-order           # 提交订单
├── GET    /temu/callback          # OAuth 回调（无需认证）
├── [JWT]  /auth/me                # 获取当前用户
├── [JWT]  /temu/auth              # 生成OAuth授权链接
├── [JWT]  /dashboard/*            # 大屏（基础版）
├── [JWT]  /pricing/*              # 核价（专业版）
├── [JWT]  /inventory/*            # 库存（基础版）
├── [JWT]  /api-sync/*             # API同步（专业版）
├── [JWT]  /scheduler/*            # 调度器（专业版）
├── [JWT]  /admin/*                # 管理后台（终身版）
└── ...
```

**注意事项**：
- [route.go](file:///d:\develop\code\temu_tools_go\internal\api\route.go) 大括号嵌套复杂，修改时必须小心闭括号平衡
- **禁止多次 SearchReplace 修改此文件**，建议一次完整重写或只做 1 次精确替换
- 改完后立即 `go build ./...` 验证

### 4.2 认证系统

在 [jwt.go](file:///d:\develop\code\temu_tools_go\internal\auth\jwt.go)：
- HS256 签名
- Claims：`UserID` + `PlanType` + 标准 JWT claims
- Token 过期时间：`.env` 中 `TOKEN_EXPIRE`（默认 24 小时）

中间件在 [middleware/auth.go](file:///d:\develop\code\temu_tools_go\internal\api\middleware\auth.go)：
- `AuthMiddleware` — 校验 JWT，将 `user_id` 和 `plan_type` 注入 context
- `PlanGuardMiddleware(page)` — 校验套餐权限，按 `PlanLevel` 层级比较

套餐等级：`basic(0) < pro(1) < enterprise(2) < lifetime(3)`

### 4.3 Temu API 客户端

在 [internal/temu/client.go](file:///d:\develop\code\temu_tools_go\internal\temu\client.go)：
- `ApiClient` 接口：25 个 API 方法
- `RealClient`：真实调用 Temu API
- `MockClient`：模拟数据，零 API 依赖

**签名算法**：
```
MD5(secret + key1value1key2value2... + secret) → 大写 hex
```
- ASCII 排序
- bool 转小写 `true`/`false`
- list/dict 用紧凑 JSON（`separators=(',',':')`）

**API 请求规范**：
- URL：`POST https://openapi-b-{region}.temu.com/openapi/router?app_secret=xxx`
- Content-Type：`application/json`
- 公共参数：`type` / `app_key` / `access_token` / `sign` / `timestamp` / `data_type`

**5 个区域**：

| 区域 | 网关 |
|------|------|
| us | `openapi-b-us.temu.com` |
| eu | `openapi-b-eu.temu.com` |
| global | `openapi-b-global.temu.com` |
| cn | `openapi.kuajingmaihuo.com` |
| pa | `openapi-b-partner.temu.com` |

### 4.4 数据库

MySQL 8.0，GORM AutoMigrate。13 张表：

| 表名 | 用途 |
|------|------|
| `temu_users` | 用户（邮箱+bcrypt密码+套餐+有效期） |
| `temu_shops` | 店铺（用户ID+店铺名） |
| `temu_shop_credentials` | 凭证（AES加密存储 access_token/api_key/secret） |
| `temu_profit_stats` | 利润统计 |
| `temu_sku_profit` | SKU利润 |
| `temu_pricing_logs` | 核价日志 |
| `temu_sync_records` | 同步记录 |
| `temu_task_definitions` | 任务定义 |
| `temu_scheduler_tasks` | 调度任务 |
| `temu_scheduler_logs` | 调度日志 |
| `temu_factory_products` | 工厂产品 |
| `temu_suppliers` | 供应商 |
| `temu_orders` | 提交订单 |

### 4.5 调度器

在 [internal/scheduler/scheduler.go](file:///d:\develop\code\temu_tools_go\internal\scheduler\scheduler.go)：
- 基于 `robfig/cron`（支持秒级精度）
- 5 个预设任务：自动同步订单/核价/库存/风控/差评
- 任务状态：registered → running → completed/failed

### 4.6 前端

React 18 + React Router 7 + Ant Design 5 + Vite。

**重要**：前端 `/` 路由是 Landing 宣传页，`/login` 是登录页，登录后跳转到 `/dashboard`。

开发模式：`cd web && npm run dev`（端口 3000，代理 API 到 8080）
生产构建：`cd web && npm run build`

**Ant Design Compatibility Note**：
- React 18 必须匹配 antd v5（React 19 + antd v5 有问题）
- 营销页（Landing/登录）用纯 HTML/CSS 实现，**不要用 Ant Design 组件**

---

## 五、数据库配置决策树

```
MySQL 在哪里？
├── 宿主机（非容器）→ DB_HOST=host.docker.internal
│   └── 需 extra_hosts: ["host.docker.internal:host-gateway"]
└── Docker 容器（temu-mysql）
    ├── 暴露了 3306 → DB_HOST=host.docker.internal
    └── 未暴露 3306 → DB_HOST=temu-mysql（需 docker network connect）
```

---

## 六、关键环境变量

`.env` 文件：

```bash
SERVER_PORT=8080
SERVER_MODE=release
SERVER_ADDRESS=0.0.0.0

DB_HOST=host.docker.internal  # 或 temu-mysql
DB_PORT=3306
DB_USER=temu
DB_PASSWORD=xxx
DB_NAME=temu_tools

JWT_SECRET=xxx                # 至少32位随机字符串
TOKEN_EXPIRE=24
ADMIN_EMAIL=admin@jinpuhuang.com
ADMIN_PASSWORD=xxx

TEMU_APP_KEY=xxx              # 从Temu Partner Platform获取
TEMU_APP_SECRET=xxx
TEMU_API_REGION=us
```

---

## 七、当前待完成工作

### P0（阻塞项）
- [ ] 等待 Temu US 自研应用"鲸云策"审核通过（目前已提交）
- [ ] 审核通过后在 Partner Platform 配置 `redirect_url` → `https://www.jinpuhuang.com/api/v1/temu/callback`
- [ ] 服务器 `.env` 配置 `TEMU_APP_KEY` / `TEMU_APP_SECRET` / `TEMU_API_REGION=us`
- [ ] 首次绑定店主店铺 LINGLINGhuang 测试连通性

### P1
- [ ] Global 区域审批（在同一个应用扩展 Global 权限）
- [ ] 服务器热更新部署（`git pull && docker compose build && docker compose up -d --no-deps app`）

### P2
- [ ] OAuth 回调后的前端提示效果完善（当前回调回 `/?success=xxx`，需在前端显示 success 消息）
- [ ] 集成测试补全（端到端 API 测试用例）
- [ ] 仓库 CRUD 表的单元测试

### P3
- [ ] 对接 Webhook（订单状态变更回调 - HMAC-SHA256 签名 + AES/CBC/PKCS5Padding 解密）
- [ ] 对接物流 API（发货/面单）
- [ ] 对接广告 API

---

## 八、已知教训与坑（避免重复踩）

### 8.1 Docker 构建缓存问题
- 前端修改后部署，必须 `docker compose build --no-cache` 强制重建
- 正常前端构建需 15-20 秒，若仅 2 秒完成说明缓存未失效

### 8.2 前端 dist/ 被 Git 排除
- `.gitignore` 的 `dist/` 会递归匹配 `web/dist/`
- 已添加 `!temu_tools_go/web/dist/` 例外规则

### 8.3 route.go 修改规则
- 大括号嵌套复杂，**禁止多次 SearchReplace**，建议一次完整重写
- 改完立即 `go build ./...` 验证

### 8.4 自研应用 vs 第三方服务商
- 自研应用：一套 App Key 服务所有店铺，每个店铺通过 OAuth 拿独立 Access Token
- 不需要注册公司主体，不需要缴纳保证金
- 不要被《转型指南》误导去走第三方服务商路线

### 8.5 OAuth 回调必备
- 必须实现回调端点接收授权 code 并自动换 token
- 当前已实现 `GET /api/v1/temu/callback`

### 8.6 跨区域密钥
- 同一个 App Key 只能绑定一个区域
- 多区域需多组 App Key 或审批后在同一个应用扩展权限

### 8.7 Landing 页同步更新
- 前端流程变更时，Landing 页、用户手册、代码三者必须同步更新

### 8.8 MySQL 严格模式
- TEXT/BLOB 类型不能设置 DEFAULT 值
- 建表 SQL 中 TEXT 字段必须去掉 `DEFAULT ''`

---

## 九、部署命令速查

### 本地开发
```bash
# 后端
cd d:\develop\code\temu_tools_go
go run ./cmd/server

# 前端
cd web && npm run dev
```

### 服务器部署
```bash
cd /opt/temu_tools_go
git pull origin master
docker compose build --no-cache && docker compose up -d --no-deps app
```

### 查看状态
```bash
docker compose ps                     # 服务状态
docker compose logs -f app --tail 30  # Go 日志
docker compose logs -f nginx --tail 10 # Nginx 日志
curl http://localhost:8080/health     # 健康检查
```

### HTTPS 证书续期（自动，但调试用）
```bash
certbot renew --dry-run  # 测试续期
```

---

## 十、测试

```bash
# 全部测试
go test ./... -count=1 -v

# 单包测试
go test ./internal/api/... -count=1 -v
go test ./internal/auth/... -count=1 -v
go test ./internal/temu/... -count=1 -v

# 集成测试（需要 MySQL 连接）
go test ./tests/... -count=1 -v
```

---

## 十一、重要文件路径速查

| 用途 | 路径 |
|------|------|
| 应用入口 | [cmd/server/main.go](file:///d:\develop\code\temu_tools_go\cmd\server\main.go) |
| 路由注册 | [internal/api/route.go](file:///d:\develop\code\temu_tools_go\internal\api\route.go) |
| Handler 逻辑 | [internal/api/handlers.go](file:///d:\develop\code\temu_tools_go\internal\api\handlers.go) |
| OAuth 回调 | [internal/api/temu_oauth.go](file:///d:\develop\code\temu_tools_go\internal\api\temu_oauth.go) |
| JWT 认证 | [internal/auth/jwt.go](file:///d:\develop\code\temu_tools_go\internal\auth\jwt.go) |
| 中间件 | [internal/api/middleware/auth.go](file:///d:\develop\code\temu_tools_go\internal\api\middleware\auth.go) |
| 数据库连接 | [internal/repository/db.go](file:///d:\develop\code\temu_tools_go\internal\repository\db.go) |
| 配置 | [internal/config/config.go](file:///d:\develop\code\temu_tools_go\internal\config\config.go) |
| GORM 模型 | [internal/models/models.go](file:///d:\develop\code\temu_tools_go\internal\models\models.go) |
| Temu API 客户端 | [internal/temu/client.go](file:///d:\develop\code\temu_tools_go\internal\temu\client.go) |
| Mock 客户端 | [internal/temu/mock.go](file:///d:\develop\code\temu_tools_go\internal\temu\mock.go) |
| 调度器 | [internal/scheduler/scheduler.go](file:///d:\develop\code\temu_tools_go\internal\scheduler\scheduler.go) |
| 服务层（大盘） | [internal/service/dashboard.go](file:///d:\develop\code\temu_tools_go\internal\service\dashboard.go) |
| 服务层（核价） | [internal/service/pricing.go](file:///d:\develop\code\temu_tools_go\internal\service\pricing.go) |
| 服务层（同步） | [internal/service/api_sync.go](file:///d:\develop\code\temu_tools_go\internal\service\api_sync.go) |
| 错误码 | [internal/api/errors.go](file:///d:\develop\code\temu_tools_go\internal\api\errors.go) |
| 前端入口 | [web/src/App.jsx](file:///d:\develop\code\temu_tools_go\web\src\App.jsx) |
| 前端 API 封装 | [web/src/api/client.js](file:///d:\develop\code\temu_tools_go\web\src\api\client.js) |
| 前端构建 | [web/vite.config.js](file:///d:\develop\code\temu_tools_go\web\vite.config.js) |
| Docker 编排 | [docker-compose.yml](file:///d:\develop\code\temu_tools_go\docker-compose.yml) |
| Docker 构建 | [Dockerfile](file:///d:\develop\code\temu_tools_go\Dockerfile) |
| Nginx 配置 | [deploy/nginx-docker.conf](file:///d:\develop\code\temu_tools_go\deploy\nginx-docker.conf) |
| 环境变量模板 | [.env.example](file:///d:\develop\code\temu_tools_go\.env.example) |
| 集成测试 | [tests/](file:///d:\develop\code\temu_tools_go\tests) |

---

## 十二、给 Cursor 的行为规则

1. **每次对话开始，先完整阅读本文档**，了解项目最新状态
2. **改代码前先完整阅读目标文件**，确认上下文
3. **只改当前任务必需的文件**，不触碰无关模块
4. **改完代码后必须执行**：
   - `go build ./...` — 零编译错误
   - `go test ./... -count=1` — 全部通过
   - 如果改了前端：`cd web && npm run build` — 构建成功
5. **route.go 修改规则**：
   - 大括号嵌套复杂，建议一次完整重写
   - 改完立即 `go build ./...` 验证
   - 禁止多次 SearchReplace 编辑此文件
6. **远程文件修改**：必须先 `grep -n` 精确定位行号，一次只改一行，改完立刻构建验证
7. **Windows vs Linux 命令区分**：本地 Windows 用 Powershell，服务器 Linux 用 bash
8. **不要创建不必要的文档文件**，除非用户明确要求

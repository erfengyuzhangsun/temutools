# 项目规则（Go 独立项目）

## 每次对话开始前必须执行

1. 先完整阅读 `模型高效驱动提示词.md` 文件（位于项目根目录），了解项目最新状态、已完成工作、待办事项、关键配置和规范约束
2. 该文件是项目的"核心记忆库"，禁止跳过此步骤直接开始任务

## 项目位置

- **本地**：`d:\develop\code\temu_tools_go\`
- **服务器**：`/opt/temu_tools_go/`
- **远程**：`origin https://github.com/erfengyuzhangsun/temutools.git`（master 分支）
- **访问地址**：https://www.jinpuhuang.com

## 当前系统状态（2026-05-19 PII加密+订单修复+Temu审核重新提交）

- Go 服务：✅ Healthy，DB 连接成功，AutoMigrate 完成
- Nginx：✅ 正常运行（80 + 443 → Go 8080）
- HTTPS：✅ Let's Encrypt 证书已配置（到期 2026-08-15，自动续签已配置）
- HTTP→HTTPS：⏳ 暂未强制跳转，两个协议均可访问
- 注册/登录/JWT：✅ 全链路正常（管理员登录已修复）
- **DB_HOST**：✅ 改为 `temu-mysql`（Docker MySQL 容器直连）
- **外键冲突**：✅ 已删除所有不兼容外键约束，AutoMigrate 通过
- **基础版到期时间**：✅ 已修复为 30 天（线上验证通过）
- **店铺绑定**：✅ 支持手动绑定（Access Token + 区域）和 OAuth 一键授权（自动回调）
- **多密钥支持**：✅ 每个店铺可自定义 App Key/Secret，优先使用店铺级密钥，无则 fallback 到 `.env`
- **OAuth 回调**：✅ `GET /temu/callback` 接收授权 code 自动换 token 并绑定店铺；`GET /temu/auth` 生成授权链接
- **Temu API请求**：✅ URL 对齐官方规范
- **Temu 自研应用审批**：⏳ 已提交 US 区"鲸云策"，Compliance & Security Assessment 已重新提交 PII 加密截图，等待审核结果
- **PII AES-256-GCM 加密**：✅ contact_name/phone/wechat/AccessToken/AppKey/AppSecret 均加密存储
- **Order json tag 修复**：✅ Order 结构体已添加 `json:"snake_case"` tag，管理员后台订单数据正常显示
- **订单状态业务逻辑**：✅ 基础版提交即自动完成，非基础版保持待处理需管理员手动操作
- **OAuth 回调地址**：⏳ 审核通过后需在 Temu Partner Platform 配置 `https://www.jinpuhuang.com/api/v1/temu/callback`
- **消费者操作流程**：管理员配好密钥 → 系统生成授权链接 → 发给客户 → 客户点链接授权 → 自动完成绑定
- **服务器**：✅ DigitalOcean（新加坡，152.42.226.188）
- **数据迁移**：✅ 所有用户数据已从阿里云导入 DO
- **DNS**：✅ www.jinpuhuang.com 已指向 DO IP
- **HTTPS 证书**：✅ Let's Encrypt，到期 2026-08-15，自动续签已配置
- 24 个 API 端点：✅ 全部通过测试
- 前端 16 页面：✅ 全部实现（7 个基础版可访问，9 个带 🔒 锁定）

## TDD 与提交门禁（每次更新必须遵循）

**原则**：每次做功能修复或新需求，必须遵循 **TDD（测试驱动开发）**；**终测全部通过后** 才允许 `git commit` 和 `git push`。禁止「先推送再补测」。

### TDD 执行流程（不可跳步）

```
1. 明确需求 → 先写/补测试（覆盖正常路径 + 主要失败路径）
2. 实现最小代码使测试通过
3. 本地终测（见下方清单）全部 PASS
4. git add → git commit → git push
5. 给出服务器热更新命令（部署后按「迁移后验证」抽检）
```

### 测试编写要求

| 层级 | 范围 | 要求 |
|------|------|------|
| 单元测试 | `internal/*` 包 | 新增/修改逻辑须补或更新对应用例（auth、middleware、temu、repository、config 等） |
| 集成测试 | `tests/api_test.go` | 涉及 API/DB 的改动须补集成用例；本地无 MySQL 时可 SKIP，**提交前须在可连 MySQL 的环境跑通** |
| 前端 | `web/` | 改动页面/路由后执行 `npm run build`；关键流程建议手工或 Playwright 抽检 |

### 终测清单（提交与推送前必须全部通过）

**本地（Windows / PowerShell）：**

```powershell
cd d:\develop\code\temu_tools_go
go build ./...
go test ./... -count=1
# 若改了前端：
cd web; npm run build
```

**有 MySQL 时额外执行（推荐，集成测试不 SKIP）：**

```powershell
cd d:\develop\code\temu_tools_go
go test ./tests/... -count=1 -v
```

**通过标准：**

- `go build`：零错误
- `go test ./...`：无 `FAIL`（允许 `tests` 在无 DB 时 SKIP，但发布前须在服务器或本地 MySQL 跑通集成测试）
- `npm run build`：成功（改了 `web/` 时）

### 禁止事项

- ❌ 未跑终测就 `git commit` / `git push`
- ❌ 仅跑单个包测试而宣称「全量通过」
- ❌ 集成测试长期 SKIP 仍发布涉及 DB/API 的改动
- ❌ 跳过测试直接改 `route.go` 多次零碎替换

---

## 模型行为红线（交付前必须逐条对照）

- ❌ **跳过对话前文档阅读**：每次对话开始必须先完整阅读 `模型高效驱动提示词.md`，尤其是"六、教训记录"和当前状态。跳过此步骤是最高优先级错误！
- ❌ **远程猜行号改文件**：远程文件必须先用 `grep -n` 精确定位行号，不得用 `sed -n` + `nl` 猜偏移量。一次只改一行，改完立刻构建验证
- ❌ **PowerShell 和 Bash 命令混用**：Windows 用 `;`，Linux 用 `&&`，必须标注"本地"还是"服务器"
- ❌ **不查文件内容就改**：改文件前完整阅读目标代码段确认上下文
- ❌ **给复杂方案代替简单方案**：优先最小改动
- ❌ **不检查就交付**：命令发出去前逐字检查路径、分支名、参数
- ❌ **热更新命令拆分成多条让用户逐条执行**：必须一次性给出完整命令 `git stash && git pull origin master && git stash pop && docker compose build --no-cache && docker compose up -d --no-deps app`，用户只需复制粘贴一次
- ❌ **改 route.go 用 SearchReplace 多次修改**：route.go 的大括号嵌套复杂，多次 SearchReplace 会导致闭括号失衡。必须一次重写完整文件或只做 1 次精确替换后立即 `go build` 验证
- ❌ **已知问题不查教训记录**：每次遇到问题先查"六、教训记录"和"踩坑复盘"中有无同类问题，禁止重复踩坑
- ❌ **自研应用当成第三方应用设计**：Temu 自研应用是一套 App Key 服务所有店铺，不是每个客户一套密钥。每个客户通过 OAuth 授权拿自己的 Access Token
- ❌ **OAuth 流程缺回调端点**：必须实现 `GET /callback` 端点接收授权 code 并自动换 token 保存，不能只让客户手动复制粘贴
- ❌ **跨区域共享同一 App Key**：Temu 限制每个自研应用只能一个区域，多区域需要多组 App Key 或审批后扩展
- ❌ **改代码不同步更新 Landing 页和用户手册**：涉及前端流程变更，Landing 页演示、用户手册、代码三者必须同步更新
- ❌ **违反 TDD 与提交门禁**：未按上文「TDD 与提交门禁」完成终测就提交/推送
- ✅ **本地必验清单（与 TDD 终测清单一致，全部 PASS 后才可 commit/push）**：
  1. `go build ./...` — 零编译错误
  2. `go test ./... -count=1` — 全部通过（发布前建议 `go test ./tests/...` 在 MySQL 环境跑通）
  3. `cd web && npm run build` — 前端构建成功（如果改了前端文件）
  4. `git add`、`git commit`、`git push origin master`
  5. 最后给出完整部署命令 `cd /opt/temu_tools_go && git stash && git pull origin master && git stash pop && docker compose build --no-cache && docker compose up -d --no-deps app`

## Docker 部署三层检查清单（每次部署前逐条确认）

```
1. .env 文件存在？DB_HOST/DB_USER/DB_PASSWORD 正确？
2. MySQL 监听 0.0.0.0？temu@'%' 有权限？
3. docker-compose.yml 有 extra_hosts + environment 覆写？
```

## DB_HOST 选择决策树

```
MySQL 在哪里？
├── 宿主机（非容器）→ DB_HOST=host.docker.internal
│   └── 需 extra_hosts: ["host.docker.internal:host-gateway"]
└── Docker 容器（temu-mysql）
    └── MySQL 是否暴露到宿主机？
        ├── 暴露了 → DB_HOST=host.docker.internal 也可行
        └── 未暴露 → DB_HOST=temu-mysql（需 docker network connect 到同一网络）
```

## AutoMigrate 失败标准处理流程

```
1. 查所有外键约束：
   docker exec -i temu-mysql mysql -u root -p$PASS -e \
   "SELECT TABLE_NAME, CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
    WHERE REFERENCED_TABLE_SCHEMA='temu_tools' AND REFERENCED_TABLE_NAME IS NOT NULL;"

2. 一次性删除全部外键：
   docker exec -i temu-mysql mysql -u root -p$PASS -N -e \
   "SELECT CONCAT('ALTER TABLE temu_tools.', TABLE_NAME, ' DROP FOREIGN KEY ',
    CONSTRAINT_NAME, ';') FROM information_schema.KEY_COLUMN_USAGE
    WHERE REFERENCED_TABLE_SCHEMA='temu_tools' AND REFERENCED_TABLE_NAME IS NOT NULL" \
   | docker exec -i temu-mysql mysql -u root -p$PASS temu_tools

3. 重启 app 容器：docker compose up -d --no-deps --force-recreate app
```

## HTTPS（Docker + Let's Encrypt）操作流程

### 首次配置
```bash
# 1. 停 Docker Nginx
docker compose stop nginx

# 2. 申请证书（只用主域名，裸域名若未解析会失败）
certbot certonly --standalone -d www.jinpuhuang.com

# 3. 重启 Docker Nginx
docker compose up -d

# 4. 创建续期钩子（certbot 自动执行）
cat > /etc/letsencrypt/renewal-hooks/pre/stop-nginx.sh << 'SCRIPT'
#!/bin/sh
/usr/bin/docker compose -f /opt/temu_tools_go/docker-compose.yml stop nginx
SCRIPT

cat > /etc/letsencrypt/renewal-hooks/post/start-nginx.sh << 'SCRIPT'
#!/bin/sh
/usr/bin/docker compose -f /opt/temu_tools_go/docker-compose.yml up -d nginx
SCRIPT

chmod +x /etc/letsencrypt/renewal-hooks/pre/stop-nginx.sh
chmod +x /etc/letsencrypt/renewal-hooks/post/start-nginx.sh
```

### 踩坑记录
- ⚠️ certbot 的 standalone 模式需要 80 端口空闲，Docker Nginx 必须先停
- ⚠️ 裸域名（jinpuhuang.com）没有 A 记录时，不能和 www 域名一并申请，会全部失败
- ⚠️ root 用户直接执行 certbot，不要加 sudo（DO 默认 root）
- ⚠️ docker-compose.yml 必须挂载 `/etc/letsencrypt:/etc/letsencrypt:ro` 才能让 Nginx 容器读到证书
- ✅ 续期 pre-hook/post-hook 用 `/usr/bin/docker compose` 绝对路径，避免 PATH 问题
- ⚠️ AES-256-GCM 加密后的 base64 比原文长 4-5 倍，`varchar(50)`/`varchar(100)` 不够存，PII 字段统一用 `varchar(255)`
- ⚠️ Go Model 必须有 `json:"snake_case"` tag，否则 Gin 输出 PascalCase 字段名，前端 Ant Design Table 匹配不上
- ⚠️ Temu 审核截图必须用原始英文字段名，不能用别名或中文标注

## 架构规范

- **目录结构**：Go 标准布局（cmd/internal/pkg）
- **Web 框架**：Gin，路由统一在 `internal/api/route.go` 注册
- **数据库**：仅 MySQL，GORM + sql.Raw 混合模式
- **前端**：`web/` 目录下 React + Vite + Ant Design
  - 开发模式：`cd web && npm run dev`（端口 3000，代理 API 到 8080）
  - 生产构建：`cd web && npm run build`
- **认证**：JWT（access_token + refresh_token），中间件统一校验

## 部署命令速查

### 首次部署
```bash
cd /opt/temu_tools_go
cp .env.example .env
nano .env   # 设置 DB_PASSWORD, JWT_SECRET, DB_HOST=host.docker.internal
docker compose build && docker compose up -d
```

### 热更新（单条命令，不可拆分）
```bash
cd /opt/temu_tools_go && git stash && git pull origin master && git stash pop && docker compose build --no-cache && docker compose up -d --no-deps app
```

### 查看状态
```bash
docker compose ps                    # 服务状态
docker compose logs -f app --tail 30 # Go 日志
docker compose logs -f nginx --tail 10 # Nginx 日志
curl http://localhost:8080/health    # 健康检查
```

## 云主机迁移快速参考

完整方法论见 `模型高效驱动提示词.md` 第 25 节。

### 迁移前必填的架构配置矩阵
```
填好源和目标两边的：MySQL位置/DB_HOST/extra_hosts/Nginx位置/部署方式
差异项 → 抽到 .env；相同项 → 放 docker-compose.yml
```

### DB_HOST 决策树
```
MySQL 在宿主机 → DB_HOST=host.docker.internal（需 extra_hosts）
MySQL 在 Docker 容器，暴露了 3306 → DB_HOST=host.docker.internal
MySQL 在 Docker 容器，未暴露 3306 → DB_HOST=temu-mysql（需 network connect）
```

### 迁移后验证（6层，不可跳步）
```
Level 1: curl localhost:8080/health
Level 2: docker compose logs app | grep "database connected"
Level 3: curl login API → 返回 token
Level 4: curl -I https://www.domain.com
Level 5: 浏览器打开页面
Level 6: go test ./tests/ -v -count=1
```

### 回滚黄金规则
```
旧服务器至少保留 72 小时不释放
DNS 切回旧 IP = 最快回滚方式
```

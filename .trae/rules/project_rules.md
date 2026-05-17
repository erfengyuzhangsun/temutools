# 项目规则（Go 独立项目）

## 每次对话开始前必须执行

1. 先完整阅读 `模型高效驱动提示词.md` 文件（位于项目根目录），了解项目最新状态、已完成工作、待办事项、关键配置和规范约束
2. 该文件是项目的"核心记忆库"，禁止跳过此步骤直接开始任务

## 项目位置

- **本地**：`d:\develop\code\temu_tools_go\`
- **服务器**：`/opt/temu_tools_go/`
- **远程**：`origin https://github.com/erfengyuzhangsun/temutools.git`（master 分支）
- **访问地址**：http://www.jinpuhuang.com

## 当前系统状态（2026-05-17）

- Go 服务：✅ Healthy，DB 连接成功，AutoMigrate 完成
- Nginx：✅ 正常运行（80 → Go 8080）
- 注册/登录/JWT：✅ 全链路正常
- **基础版到期时间**：✅ 已修复为 30 天（线上验证通过）
- **店铺绑定**：✅ access_token 持久化到 DB
- **Temu API请求**：✅ URL 对齐官方规范
- **Temu 自研应用审批**：❌ 被拒绝（根因：阿里云 ECS）
- **服务器**：✅ 已从阿里云迁移到 DigitalOcean（新加坡，152.42.226.188）
- **数据迁移**：✅ 所有用户数据已从阿里云导入 DO
- **DNS**：⏳ 待将 www.jinpuhuang.com 指向 DO IP
- **HTTPS**：⏳ 待配置 Let's Encrypt 证书
- 24 个 API 端点：✅ 全部通过测试
- 前端 16 页面：✅ 全部实现（7 个基础版可访问，9 个带 🔒 锁定）

## 模型行为红线（交付前必须逐条对照）

- ❌ **PowerShell 和 Bash 命令混用**：Windows 用 `;`，Linux 用 `&&`，必须标注"本地"还是"服务器"
- ❌ **不查文件内容就改**：改文件前完整阅读目标代码段确认上下文
- ❌ **给复杂方案代替简单方案**：优先最小改动
- ❌ **不检查就交付**：命令发出去前逐字检查路径、分支名、参数
- ❌ **改 route.go 用 SearchReplace 多次修改**：route.go 的大括号嵌套复杂，多次 SearchReplace 会导致闭括号失衡。必须一次重写完整文件或只做 1 次精确替换后立即 `go build` 验证
- ✅ **本地必验清单（每次改代码后必须执行）**：
  1. `go build ./...` — 零编译错误
  2. `go test ./...` — 全部通过
  3. `cd web && npm run build` — 前端构建成功（如果改了前端文件）
  4. 以上全部通过后，再 `git add`、`git commit`、`git push`
  5. 最后给出部署命令 `docker compose build && docker compose up -d --no-deps app`

## Docker 部署三层检查清单（每次部署前逐条确认）

```
1. .env 文件存在？DB_HOST/DB_USER/DB_PASSWORD 正确？
2. MySQL 监听 0.0.0.0？temu@'%' 有权限？
3. docker-compose.yml 有 extra_hosts + environment 覆写？
```

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

### 热更新
```bash
cd /opt/temu_tools_go
git pull origin master
docker compose build && docker compose up -d --no-deps app
```

### 查看状态
```bash
docker compose ps                    # 服务状态
docker compose logs -f app --tail 30 # Go 日志
docker compose logs -f nginx --tail 10 # Nginx 日志
curl http://localhost:8080/health    # 健康检查
```

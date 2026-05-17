#!/bin/bash
# 首次部署初始化脚本
set -euo pipefail

cd "$(dirname "$0")/.."
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

log "==================== 首次初始化 ===================="

command -v docker >/dev/null 2>&1 || { warn "请先安装 Docker"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { warn "请先安装 Docker Compose v2"; exit 1; }

if [ ! -f .env ]; then
    warn "创建 .env 文件..."
    cp .env.example .env
    warn "请编辑 .env 配置数据库密码和 JWT_SECRET"
    exit 1
fi

log "构建 Docker 镜像..."
docker compose build

log "启动所有服务..."
docker compose up -d

log "服务启动中..."
sleep 5
docker compose ps

log "==================== 初始化完成 ===================="
log "后续更新执行: docker compose build && docker compose up -d"
log "查看日志: docker compose logs -f app"

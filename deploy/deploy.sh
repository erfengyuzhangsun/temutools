#!/bin/bash
# ===== Temu Tools Go 热更新部署脚本 =====
set -euo pipefail

cd "$(dirname "$0")/.."
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; }

if [ ! -f .env ]; then
    err "缺少 .env 配置文件"
    exit 1
fi

log "==================== 热更新 ===================="

log "Step 1/3: 拉取最新代码..."
git pull origin main 2>/dev/null || true

log "Step 2/3: 构建新镜像..."
docker compose build

log "Step 3/3: 滚动更新（零停机）..."
docker compose up -d --no-deps --scale nginx=1 app

log "等待健康检查..."
sleep 5
docker compose ps

log "==================== 更新完成 ===================="

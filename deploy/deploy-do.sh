#!/bin/bash
# ===== DigitalOcean 一键迁移部署脚本 =====
# 用法:
#   方式1（推荐）: 传入 GitHub Token
#     export GITHUB_TOKEN=你的token
#     bash deploy/deploy-do.sh
#
#   方式2: 作为参数传入
#     bash deploy/deploy-do.sh 你的GitHubToken
#
#   方式3: 交互式输入（脚本会提示）
#     bash deploy/deploy-do.sh
#
# GitHub Token 获取: https://github.com/settings/tokens -> 勾选 repo 权限
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; }
info() { echo -e "${BLUE}[i]${NC} $1"; }
sep()  { echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }

PROJECT_DIR="/opt/temu_tools_go"
GIT_REPO="https://github.com/erfengyuzhangsun/temutools.git"
DOMAIN="www.jinpuhuang.com"
NETWORK_NAME="temu-net"
MYSQL_CONTAINER="temu-mysql"

sep
echo -e "${BLUE}  DigitalOcean 一键迁移部署${NC}"
echo -e "${BLUE}  项目: Temu Tools Go${NC}"
sep

# ============================================
# Step 0: GitHub 认证配置
# ============================================
log "Step 0/9: 配置 GitHub 访问..."
GITHUB_TOKEN="${1:-${GITHUB_TOKEN:-}}"
if [ -z "$GITHUB_TOKEN" ]; then
    warn "未检测到 GitHub Token"
    warn "仓库 erfengyuzhangsun/temutools 是私有的，需要 Token 才能拉取代码"
    echo ""
    echo -e "  如何获取 Token:"
    echo -e "    1. 打开 https://github.com/settings/tokens"
    echo -e "    2. 点击 Generate new token → Generate new token (classic)"
    echo -e "    3. 勾选 repo 权限（全选）"
    echo -e "    4. 生成后复制 token 字符串"
    echo ""
    read -rsp "  请输入你的 GitHub Token: " GITHUB_TOKEN
    echo ""
    if [ -z "$GITHUB_TOKEN" ]; then
        err "Token 不能为空，退出"
        exit 1
    fi
fi

# 配置 Git 使用 Token 认证
git config --global credential.helper "store --file ~/.git-credentials"
echo "https://erfengyuzhangsun:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
log "GitHub 认证已配置"

# ============================================
# Step 1: 系统初始化
# ============================================
log "Step 1/9: 系统初始化..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq curl wget git ufw certbot python3-certbot-nginx openssl

# ============================================
# Step 2: 安装 Docker
# ============================================
log "Step 2/9: 安装 Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
    log "Docker 安装完成"
fi

# ============================================
# Step 3: 配置防火墙
# ============================================
log "Step 3/9: 配置防火墙..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
log "防火墙已配置"

# ============================================
# Step 4: 创建 Docker 网络
# ============================================
log "Step 4/9: 创建 Docker 网络..."
docker network inspect "$NETWORK_NAME" &>/dev/null || \
    docker network create "$NETWORK_NAME"
log "Docker 网络已就绪"

# ============================================
# Step 5: 拉取代码
# ============================================
log "Step 5/9: 拉取代码..."
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    git fetch origin
    git checkout master
    git pull origin master
    log "代码已更新"
else
    mkdir -p "$PROJECT_DIR"
    git clone "$GIT_REPO" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    git checkout master
    log "代码已克隆"
fi

# ============================================
# Step 6: 配置 .env
# ============================================
log "Step 6/9: 配置环境变量..."
cd "$PROJECT_DIR"

if [ ! -f .env ]; then
    cp .env.example .env

    DB_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 20)
    JWT_SECRET=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 40)
    ADMIN_PASS=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 16)
    ENC_KEY=$(openssl rand -base64 32)

    sed -i "s/DB_PASSWORD=your_db_password_here/DB_PASSWORD=$DB_PASS/" .env
    sed -i "s|JWT_SECRET=change_me_to_a_random_string_at_least_32_chars|JWT_SECRET=$JWT_SECRET|" .env
    sed -i "s/ADMIN_PASSWORD=your_admin_password_here/ADMIN_PASSWORD=$ADMIN_PASS/" .env
    sed -i "s|ENCRYPTION_KEY=your_encryption_key_at_least_32_chars_long_here|ENCRYPTION_KEY=$ENC_KEY|" .env
    sed -i "s/DB_HOST=host.docker.internal/DB_HOST=$MYSQL_CONTAINER/" .env

    log ".env 已生成"
    info "DB_PASSWORD:  $DB_PASS"
    info "JWT_SECRET:   $JWT_SECRET"
    info "ENCRYPTION_KEY: $ENC_KEY"
    info "ADMIN_PASSWORD: $ADMIN_PASS"
    warn "请保存以上密码和密钥！仅首次显示"
else
    log ".env 已存在, 跳过"
fi

# 读取 DB 密码供后续使用
source .env 2>/dev/null || true
DB_PASSWORD=$(grep ^DB_PASSWORD= .env | head -1 | cut -d= -f2-)

# ============================================
# Step 7: 启动 MySQL 容器
# ============================================
log "Step 7/9: 部署 MySQL..."
if ! docker ps --format '{{.Names}}' | grep -q "^$MYSQL_CONTAINER$"; then
    docker run -d \
        --name "$MYSQL_CONTAINER" \
        --restart unless-stopped \
        --network "$NETWORK_NAME" \
        -e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" \
        -e MYSQL_DATABASE=temu_tools \
        -e MYSQL_USER=temu \
        -e MYSQL_PASSWORD="$DB_PASSWORD" \
        -v temu-mysql-data:/var/lib/mysql \
        mysql:8.0 \
        --character-set-server=utf8mb4 \
        --collation-server=utf8mb4_unicode_ci \
        --default-authentication-plugin=mysql_native_password

    log "MySQL 容器启动中 (等待 20s 初始化)..."
    sleep 20

    # 确保 temu@'%' 有权限
    docker exec "$MYSQL_CONTAINER" mysql -u root -p"$DB_PASSWORD" -e "
        ALTER USER 'temu'@'%' IDENTIFIED BY '$DB_PASSWORD';
        FLUSH PRIVILEGES;
    " 2>/dev/null || true

    log "MySQL 部署完成 ✅"
else
    log "MySQL 已运行, 跳过"
fi

# 确保网络已连接
docker network connect "$NETWORK_NAME" "$MYSQL_CONTAINER" 2>/dev/null || true

# ============================================
# Step 7.5: 数据迁移（可选）
# ============================================
log "Step 7.5/9: 数据迁移（可选）..."
if [ -f /tmp/temu_tools_export.sql ] || [ -f /tmp/temu_tools_export.sql.gz ]; then
    log "检测到阿里云导出文件，自动导入数据..."
    bash "$PROJECT_DIR/deploy/deploy-migrate-db.sh" import /tmp/temu_tools_export.sql.gz 2>/dev/null || \
    bash "$PROJECT_DIR/deploy/deploy-migrate-db.sh" import /tmp/temu_tools_export.sql 2>/dev/null || true
else
    info "未检测到数据文件，跳过迁移"
    info "如需迁移阿里云数据，请在部署完成后执行："
    info "  # 1. 阿里云上导出:  bash deploy/deploy-migrate-db.sh export"
    info "  # 2. 传到 DO:       scp /tmp/temu_tools_export.sql.gz root@你的DO_IP:/tmp/"
    info "  # 3. DO 上导入:     bash deploy/deploy-migrate-db.sh import /tmp/temu_tools_export.sql.gz"
fi

# ============================================
# Step 8: 构建 & 启动 Go + Nginx
# ============================================
log "Step 8/9: 构建并启动服务..."
cd "$PROJECT_DIR"

# 构建镜像
docker compose build --no-cache 2>&1 | tail -3 || docker compose build 2>&1 | tail -3

# 将 app 和 nginx 加入同一网络
export COMPOSE_PROJECT_NAME=temu
docker compose up -d

# 连接网络
docker network connect "$NETWORK_NAME" temu-tools-go 2>/dev/null || true
docker network connect "$NETWORK_NAME" temu-tools-nginx 2>/dev/null || true

# 等待服务就绪
log "等待服务就绪..."
for i in $(seq 1 15); do
    sleep 3
    if curl -s http://localhost:8080/health 2>/dev/null | grep -q '"ok"'; then
        log "Go 服务健康 ✅"
        break
    fi
    if [ "$i" -eq 15 ]; then
        warn "Go 服务未就绪, 检查日志: docker compose logs app --tail 30"
    fi
done

# 重启 Nginx 使配置生效
docker compose restart nginx 2>/dev/null || true

# ============================================
# Step 9: HTTPS 配置
# ============================================
log "Step 9/9: HTTPS (Let's Encrypt)..."
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || curl -s https://api.ipify.org 2>/dev/null || echo "unknown")
info "服务器公网 IP: $PUBLIC_IP"

# 检查 DNS 是否指向本机
DNS_CHECK=$(curl -sI "http://$DOMAIN" 2>/dev/null | head -1 || echo "")
if echo "$DNS_CHECK" | grep -q "200\|301\|302"; then
    log "域名 DNS 已生效, 申请 SSL 证书..."
    certbot --nginx -d "$DOMAIN" -d "jinpuhuang.com" \
        --non-interactive --agree-tos -m "admin@jinpuhuang.com" || warn "证书申请失败, 稍后手动执行"
    docker compose restart nginx
    log "HTTPS 配置完成 ✅"
else
    warn "域名 DNS 尚未指向本机"
    info "请将 $DOMAIN 的 A 记录指向: $PUBLIC_IP"
    info "DNS 生效后执行:  sudo certbot --nginx -d $DOMAIN -d jinpuhuang.com"
fi

# ============================================
# 最终验证
# ============================================
sep
echo -e "${GREEN}  🎉 迁移部署完成！${NC}"
sep
echo ""
echo -e "  ${BLUE}HTTP:${NC}    http://$DOMAIN"
echo -e "  ${BLUE}项目:${NC}    $PROJECT_DIR"
echo ""
echo -e "  ${YELLOW}管理员登录:${NC}"
echo -e "    邮箱: admin@jinpuhuang.com"
echo -e "    密码: $(grep ^ADMIN_PASSWORD= $PROJECT_DIR/.env | head -1 | cut -d= -f2-)"
echo ""
echo -e "  ${YELLOW}常用命令:${NC}"
echo -e "    查看日志:   docker compose -f $PROJECT_DIR/docker-compose.yml logs -f app --tail 30"
echo -e "    热更新:     cd $PROJECT_DIR && git pull && docker compose build && docker compose up -d"
echo -e "    MySQL 连接: docker exec -it $MYSQL_CONTAINER mysql -u temu -p"
echo ""
echo -e "  ${YELLOW}后续操作:${NC}"
echo -e "    1. 配置 DNS: $DOMAIN → $PUBLIC_IP (如未配置)"
echo -e "    2. 配置 TEMU_APP_KEY / TEMU_APP_SECRET: nano $PROJECT_DIR/.env"
echo -e "    3. 重新提交 Temu 自研应用审批 (服务器=新加坡, AWS→实际用DO)"
echo -e "    4. 重启容器: docker compose restart app"
sep

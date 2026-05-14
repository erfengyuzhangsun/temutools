#!/bin/bash
# ============================================================
# Temu全托管运营平台 - 阿里云ECS一键部署脚本
# 适用系统: Ubuntu 20.04/22.04 / CentOS 7/8 / Alibaba Cloud Linux
# 用法:
#   chmod +x deploy_aliyun.sh
#   sudo bash deploy_aliyun.sh
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 项目配置
PROJECT_DIR="/opt/temu_tools"
GIT_REPO=""  # 留空则使用当前目录拷贝，填写则自动git clone
BRANCH="main"
STREAMLIT_PORT=8501

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "\n${BLUE}========================================${NC}"; echo -e "${BLUE}[$1/$2]${NC} $3"; echo -e "${BLUE}========================================${NC}"; }

# ==================== 检查root权限 ====================
if [[ $EUID -ne 0 ]]; then
    log_error "请使用 sudo 或 root 用户运行此脚本"
    exit 1
fi

TOTAL_STEPS=10

# ==================== 检测操作系统 ====================
log_step 1 $TOTAL_STEPS "检测操作系统"

OS=""
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    if [[ "$ID" == "ubuntu" || "$ID_LIKE" == *"ubuntu"* ]]; then
        OS="ubuntu"
    elif [[ "$ID" == "centos" || "$ID" == "alinux" || "$ID_LIKE" == *"centos"* ]]; then
        OS="centos"
    fi
fi

if [[ -z "$OS" ]]; then
    log_error "不支持的操作系统，仅支持 Ubuntu / CentOS / Alibaba Cloud Linux"
    exit 1
fi
log_info "检测到操作系统: $ID $VERSION_ID"

PKG_UPDATE=""
PKG_INSTALL=""
MYSQL_SERVICE=""
MYSQL_CONF=""

if [[ "$OS" == "ubuntu" ]]; then
    PKG_UPDATE="apt-get update -y"
    PKG_INSTALL="apt-get install -y"
    MYSQL_SERVICE="mysql"
    MYSQL_CONF="/etc/mysql/mysql.conf.d/mysqld.cnf"
elif [[ "$OS" == "centos" ]]; then
    PKG_UPDATE="yum update -y"
    PKG_INSTALL="yum install -y"
    MYSQL_SERVICE="mysqld"
    MYSQL_CONF="/etc/my.cnf"
fi

# ==================== 安装系统依赖 ====================
log_step 2 $TOTAL_STEPS "安装系统依赖包"

$PKG_UPDATE
if [[ "$OS" == "ubuntu" ]]; then
    $PKG_INSTALL python3 python3-pip python3-venv git curl wget mysql-server mysql-client nginx
elif [[ "$OS" == "centos" ]]; then
    $PKG_INSTALL python3 python3-pip git curl wget mysql-server mysql nginx
fi


# ==================== 配置MySQL ====================
log_step 3 $TOTAL_STEPS "配置MySQL数据库"

systemctl start $MYSQL_SERVICE
systemctl enable $MYSQL_SERVICE

# 等待MySQL启动
sleep 3
if ! systemctl is-active --quiet $MYSQL_SERVICE; then
    log_error "MySQL启动失败，请检查日志: journalctl -u $MYSQL_SERVICE"
    exit 1
fi
log_info "MySQL已启动"

# 创建数据库和用户
DB_NAME="temu_tools"
DB_USER="temu"
DB_PASS=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -16)

if [[ "$OS" == "ubuntu" ]]; then
    mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF
elif [[ "$OS" == "centos" ]]; then
    # CentOS默认有临时密码，尝试无密码登录
    mysql <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF
fi

log_info "数据库 ${DB_NAME} 创建成功"
log_info "数据库用户: ${DB_USER} / 密码: ${DB_PASS}"

# 优化MySQL配置（适配2核4G ECS）
cat >> $MYSQL_CONF <<EOF

# Temu优化配置
[mysqld]
max_connections = 200
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
EOF

systemctl restart $MYSQL_SERVICE
log_info "MySQL优化配置已完成"

# ==================== 部署项目代码 ====================
log_step 4 $TOTAL_STEPS "部署项目代码"

# 如果已经存在项目目录，则备份
if [[ -d "$PROJECT_DIR" ]]; then
    BACKUP_DIR="${PROJECT_DIR}_backup_$(date +%Y%m%d%H%M%S)"
    log_warn "项目目录已存在，备份到 ${BACKUP_DIR}"
    mv "$PROJECT_DIR" "$BACKUP_DIR"
fi

mkdir -p "$PROJECT_DIR"

# 获取代码
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -f "$SCRIPT_DIR/app.py" ]]; then
    # 脚本在当前项目目录中运行，直接拷贝
    log_info "检测到本地项目文件，直接拷贝..."
    cp -r "$SCRIPT_DIR"/* "$PROJECT_DIR/"
    cp "$SCRIPT_DIR"/.env.example "$PROJECT_DIR/.env" 2>/dev/null || true
else
    # 提示用户手动上传代码
    log_warn "未检测到本地项目文件"
    echo ""
    echo "请选择代码部署方式:"
    echo "  1) 输入Git仓库地址自动克隆"
    echo "  2) 手动上传代码到 ${PROJECT_DIR}"
    read -p "请选择 (1/2，默认2): " DEPLOY_CHOICE
    DEPLOY_CHOICE=${DEPLOY_CHOICE:-2}

    if [[ "$DEPLOY_CHOICE" == "1" ]]; then
        read -p "请输入Git仓库地址: " GIT_REPO
        if [[ -n "$GIT_REPO" ]]; then
            git clone -b "$BRANCH" "$GIT_REPO" "$PROJECT_DIR"
            log_info "代码克隆完成"
        else
            log_error "仓库地址不能为空"
            exit 1
        fi
    else
        echo ""
        log_warn "请在另一个终端执行以下命令上传代码:"
        echo "  scp -r /path/to/temu_tools/* root@你的IP:${PROJECT_DIR}/"
        echo ""
        read -p "上传完成后按回车键继续..."
        if [[ ! -f "$PROJECT_DIR/app.py" ]]; then
            log_error "未检测到项目文件，请确保上传到 ${PROJECT_DIR}"
            exit 1
        fi
    fi
fi

# 复制 .env.example 到 .env（如不存在）
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env" 2>/dev/null || true
fi

cd "$PROJECT_DIR"
log_info "项目代码已部署到 ${PROJECT_DIR}"

# ==================== 安装Python依赖 ====================
log_step 5 $TOTAL_STEPS "安装Python依赖"

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # 生产环境用gunicorn
log_info "Python依赖安装完成"

# ==================== 生成加密密钥 ====================
log_step 6 $TOTAL_STEPS "生成加密密钥"

ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
log_info "加密密钥已生成"

# ==================== 配置环境变量 ====================
log_step 7 $TOTAL_STEPS "配置环境变量"

cat > "$PROJECT_DIR/.env" <<EOF
# Temu全托管运营平台 - 环境配置
DB_MODE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=${DB_USER}
MYSQL_PASSWORD=${DB_PASS}
MYSQL_DATABASE=${DB_NAME}
ADMIN_PASSWORD=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -12)
SEED_ADMIN_PASSWORD=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -12)
ENCRYPTION_KEY=${ENCRYPTION_KEY}
PORT=${STREAMLIT_PORT}
ADDRESS=0.0.0.0
EOF

log_info "环境变量已配置到 .env"
ADMIN_PASSWORD=$(grep "^ADMIN_PASSWORD=" "$PROJECT_DIR/.env" | cut -d= -f2)
SEED_PASSWORD=$(grep "^SEED_ADMIN_PASSWORD=" "$PROJECT_DIR/.env" | cut -d= -f2)

# ==================== 初始化数据库 ====================
log_step 8 $TOTAL_STEPS "初始化数据库表"

source "$PROJECT_DIR/venv/bin/activate"
cd "$PROJECT_DIR"
python3 startup.py --init-only

log_info "数据库初始化完成"

# ==================== 配置systemd服务（开机自启） ====================
log_step 9 $TOTAL_STEPS "配置systemd服务（开机自启）"

cat > /etc/systemd/system/temu-tools.service <<EOF
[Unit]
Description=Temu全托管运营平台
After=network.target mysql.service mariadb.service
Wants=mysql.service mariadb.service

[Service]
Type=simple
User=root
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${PROJECT_DIR}/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
ExecStart=${PROJECT_DIR}/venv/bin/python -m streamlit run app.py --server.port ${STREAMLIT_PORT} --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
Restart=always
RestartSec=10
StandardOutput=append:${PROJECT_DIR}/logs/app.log
StandardError=append:${PROJECT_DIR}/logs/app.log

[Install]
WantedBy=multi-user.target
EOF

mkdir -p "$PROJECT_DIR/logs"
systemctl daemon-reload
systemctl enable temu-tools.service
systemctl start temu-tools.service

log_info "systemd服务已配置并启动"

# ==================== 配置Nginx反向代理（可选）====================
log_step 10 $TOTAL_STEPS "配置Nginx反向代理"

echo ""
log_info "是否配置 Nginx 反向代理 + HTTPS？"
echo "  配置后可通过 http://你的域名 或 https://你的域名 访问"
echo "  不配置则直接通过 http://你的IP:${STREAMLIT_PORT} 访问"
echo ""
read -p "是否配置Nginx? (y/n，默认n): " NGINX_CHOICE

if [[ "$NGINX_CHOICE" == "y" || "$NGINX_CHOICE" == "Y" ]]; then
    read -p "请输入你的域名 (如 temu.example.com): " DOMAIN_NAME

    # 安装SSL证书（acme.sh）
    curl https://get.acme.sh | sh
    ~/.acme.sh/acme.sh --set-default-ca --server letsencrypt

    # 先配置HTTP临时站点用于申请证书
    cat > /etc/nginx/conf.d/temu-tools.conf <<EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME};

    location / {
        proxy_pass http://127.0.0.1:${STREAMLIT_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

    systemctl reload nginx

    # 申请SSL证书
    ~/.acme.sh/acme.sh --issue -d "$DOMAIN_NAME" --nginx

    if [[ -f ~/.acme.sh/${DOMAIN_NAME}/fullchain.cer ]]; then
        # 配置HTTPS
        cat > /etc/nginx/conf.d/temu-tools.conf <<EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME};
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN_NAME};

    ssl_certificate ~/.acme.sh/${DOMAIN_NAME}/fullchain.cer;
    ssl_certificate_key ~/.acme.sh/${DOMAIN_NAME}/${DOMAIN_NAME}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:${STREAMLIT_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    # Streamlit的WebSocket支持
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:${STREAMLIT_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }
}
EOF
        systemctl reload nginx
        log_info "HTTPS配置完成！https://${DOMAIN_NAME}"
    else
        log_warn "SSL证书申请失败，请稍后手动配置"
    fi
else
    log_info "跳过Nginx配置，直接通过 http://你的服务器IP:${STREAMLIT_PORT} 访问"
fi

# ==================== 完成 ====================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "  ${BLUE}应用地址:${NC}  http://$(curl -s ifconfig.me):${STREAMLIT_PORT}"
echo -e "  ${BLUE}访问密码:${NC}  ${SEED_PASSWORD}"
echo -e "  ${BLUE}管理员密码:${NC} ${ADMIN_PASSWORD}"
echo ""
echo -e "  ${YELLOW}数据库信息${NC}"
echo -e "  ───────────────────────────────"
echo -e "  数据库: ${DB_NAME}"
echo -e "  用户名: ${DB_USER}"
echo -e "  密  码: ${DB_PASS}"
echo ""
echo -e "  ${YELLOW}⚠️  安全须知${NC}"
echo -e "  ───────────────────────────────"
echo -e "  🔴 请立即保存以上密码，关闭终端后将无法找回！"
echo -e "  🔴 首次登录后请在管理后台修改密码"
echo -e "  🔴 .env 文件包含敏感信息，严禁提交到 Git"

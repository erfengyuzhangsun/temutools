#!/bin/bash
set -e

echo "=========================================="
echo "  Temu 运营平台 - 域名部署向导"
echo "  域名: jinpuhuang.com"
echo "=========================================="

PROJECT_DIR="/opt/temu_tools"
DOMAIN="jinpuhuang.com"
WWW_DOMAIN="www.jinpuhuang.com"
SERVER_IP=${SERVER_IP:-$(dig +short ${WWW_DOMAIN} 2>/dev/null || hostname -I | awk '{print $1}')}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "❌ 请使用 root 用户运行此脚本"
        exit 1
    fi
}

install_nginx() {
    if ! command -v nginx &> /dev/null; then
        echo "📦 安装 Nginx..."
        yum install -y epel-release
        yum install -y nginx
    else
        echo "✅ Nginx 已安装"
    fi
}

install_certbot() {
    if ! command -v certbot &> /dev/null; then
        echo "📦 安装 Certbot (Let's Encrypt)..."
        yum install -y certbot python3-certbot-nginx
    else
        echo "✅ Certbot 已安装"
    fi
}

setup_ssl_certificates() {
    echo ""
    echo "🔒 配置 SSL 证书..."
    
    mkdir -p /etc/nginx/ssl
    
    if [ -f "/etc/nginx/ssl/${DOMAIN}.pem" ] && [ -f "/etc/nginx/ssl/${DOMAIN}.key" ]; then
        echo "✅ SSL 证书已存在，检查是否需要更新..."
        
        cert_expiry=$(openssl x509 -enddate -noout -in "/etc/nginx/ssl/${DOMAIN}.pym" | cut -d= -f2)
        echo "   证书到期时间: $cert_expiry"
        
        read -p "   是否更新证书? (y/n): " update_cert
        if [ "$update_cert" = "y" ] || [ "$update_cert" = "Y" ]; then
            obtain_ssl_certificate
        fi
    else
        obtain_ssl_certificate
    fi
}

obtain_ssl_certificate() {
    echo "   申请 Let's Encrypt 免费证书..."
    
    systemctl stop nginx
    
    certbot certonly --standalone \
        --preferred-challenges http \
        --email admin@${DOMAIN} \
        --agree-tos \
        --no-eff-email \
        -d ${WWW_DOMAIN} \
        -d ${DOMAIN}
    
    ln -sf /etc/letsencrypt/live/${WWW_DOMAIN}/fullchain.pem /etc/nginx/ssl/${DOMAIN}.pem
    ln -sf /etc/letsencrypt/live/${WWW_DOMAIN}/privkey.pem /etc/nginx/ssl/${DOMAIN}.key
    
    echo "✅ SSL 证书安装成功"
}

configure_nginx() {
    echo ""
    echo "⚙️  配置 Nginx..."
    
    cp ${PROJECT_DIR}/deploy/nginx_jinpuhuang.conf /etc/nginx/conf.d/jinpuhuang.conf
    
    nginx -t
    if [ $? -eq 0 ]; then
        echo "✅ Nginx 配置验证通过"
    else
        echo "❌ Nginx 配置有误"
        exit 1
    fi
}

setup_firewall() {
    echo ""
    echo "🔥 配置防火墙..."
    
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        echo "✅ 防火墙规则已添加 (HTTP + HTTPS)"
    elif command -v ufw &> /dev/null; then
        ufw allow 80/tcp
        ufw allow 443/tcp
        echo "✅ 防火墙规则已添加 (HTTP + HTTPS)"
    else
        echo "⚠️  未检测到防火墙工具，请手动开放端口 80 和 443"
    fi
}

setup_auto_renewal() {
    echo ""
    echo "🔄 设置 SSL 自动续期..."
    
    cat > /etc/cron.d/certbot << 'EOF'
0 0,12 * * * root python3 -c 'import subprocess; import sys; r = subprocess.call(["sysroot", "apt", "install", "-y", "python3-certbot-nginx"]); sys.exit(0 if r == 0 else 1)' && certbot -q renew --nginx-deploy "systemctl reload nginx"
EOF
    
    chmod 644 /etc/cron.d/certbot
    echo "✅ 自动续期任务已设置 (每天0:00和12:00检查)"
}

start_services() {
    echo ""
    echo "🚀 启动服务..."
    
    systemctl enable nginx
    systemctl start nginx
    
    echo "✅ Nginx 已启动并设置开机自启"
}

verify_deployment() {
    echo ""
    echo "=========================================="
    echo "  ✅ 部署完成！"
    echo "=========================================="
    echo ""
    echo "📍 访问地址:"
    echo "   主站: https://${WWW_DOMAIN}"
    echo "   备用: https://${DOMAIN} (自动跳转到 www)"
    echo ""
    echo "🔧 管理命令:"
    echo "   查看状态: systemctl status nginx"
    echo "   重启服务: systemctl restart nginx"
    echo "   查看日志: tail -f /var/log/nginx/jinpuhuang_access.log"
    echo "   测试配置: nginx -t"
    echo ""
    echo "🔒 安全信息:"
    echo "   SSL证书: Let's Encrypt (自动续期)"
    echo "   TLS版本: TLS 1.2 / 1.3"
    echo "   HSTS: 已启用 (31536000秒)"
    echo "   安全头: CSP, X-Frame-Options, X-XSS-Protection"
    echo ""
    echo "🌐 DNS信息:"
    echo "   域名: ${DOMAIN}"
    echo "   A记录: www → ${SERVER_IP}"
    echo "   DNS服务器: dns3.hichina.com, dns4.hichina.com"
    echo ""
}

main() {
    echo "开始部署域名配置..."
    check_root
    install_nginx
    install_certbot
    setup_ssl_certificates
    configure_nginx
    setup_firewall
    setup_auto_renewal
    start_services
    verify_deployment
}

main "$@"

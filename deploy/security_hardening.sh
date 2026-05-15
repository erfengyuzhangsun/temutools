#!/bin/bash
set -e

echo "=========================================="
echo "  企业级安全加固脚本"
echo "  Temu 运营平台 - jinpuhuang.com"
echo "=========================================="

PROJECT_DIR="/opt/temu_tools"
LOG_DIR="${PROJECT_DIR}/logs"

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "❌ 请使用 root 用户运行此脚本"
        exit 1
    fi
}

secure_ssh() {
    echo ""
    echo "🔒 加固 SSH 配置..."
    
    SSH_CONFIG="/etc/ssh/sshd_config"
    
    cp ${SSH_CONFIG} ${SSH_CONFIG}.bak.$(date +%Y%m%d)
    
    sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' ${SSH_CONFIG}
    sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' ${SSH_CONFIG}
    sed -i 's/^#*PubkeyAuthentication.*/PubkeyAuthentication yes/' ${SSH_CONFIG}
    
    if ! grep -q "^MaxAuthTries" ${SSH_CONFIG}; then
        echo "MaxAuthTries 3" >> ${SSH_CONFIG}
    else
        sed -i 's/^MaxAuthTries.*/MaxAuthTries 3/' ${SSH_CONFIG}
    fi
    
    if ! grep -q "^ClientAliveInterval" ${SSH_CONFIG}; then
        echo "ClientAliveInterval 300" >> ${SSH_CONFIG}
    fi
    
    if ! grep -q "^AllowUsers" ${SSH_CONFIG}; then
        echo "# AllowUsers your_username" >> ${SSH_CONFIG}
    fi
    
    systemctl restart sshd
    echo "✅ SSH 安全加固完成"
}

secure_system() {
    echo ""
    echo "🛡️  系统安全加固..."
    
    echo "* 设置文件权限..."
    chmod 700 /root
    chmod 600 /etc/shadow
    
    echo "* 禁用不必要的端口..."
    systemctl disable --now telnet.socket || true
    
    echo "* 安装安全更新..."
    yum update -y security || yum update -y
    
    echo "* 安装 fail2ban..."
    if ! command -v fail2ban-client &> /dev/null; then
        yum install -y fail2ban
        systemctl enable fail2ban
        systemctl start fail2ban
    fi
    
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/secure
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
EOF
    
    systemctl restart fail2ban
    echo "✅ 系统安全加固完成"
}

configure_firewall_rules() {
    echo ""
    echo "🔥 配置防火墙规则..."
    
    if command -v firewall-cmd &> /dev/null; then
        
        firewall-cmd --permanent --remove-service=ssh || true
        firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="YOUR_TRUSTED_IP/32" service name="ssh" accept'
        
        firewall-cmd --permanent --add-port=8501/tcp
        
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        
        firewall-cmd --permanent --add-icmp-block=echo-request || true
        
        firewall-cmd --reload
        
        echo "✅ 防火墙规则已配置"
        echo "   ⚠️  请将 YOUR_TRUSTED_IP 替换为你的实际IP地址"
    fi
}

setup_log_rotation() {
    echo ""
    echo "📋 配置日志轮转..."
    
    cat > /etc/logrotate.d/temu-tools << EOF
${LOG_DIR}/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root adm
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
EOF
    
    echo "✅ 日志轮转已配置 (保留14天)"
}

setup_security_headers() {
    echo ""
    echo "🔐 检查安全头配置..."
    
    NGINX_CONF="/etc/nginx/conf.d/jinpuhuang.conf"
    
    if [ -f "${NGINX_CONF}" ]; then
        if grep -q "Strict-Transport-Security" ${NGINX_CONF} && \
           grep -q "X-Frame-Options" ${NGINX_CONF} && \
           grep -q "Content-Security-Policy" ${NGINX_CONF}; then
            echo "✅ 安全头已正确配置"
        else
            echo "⚠️  安全头配置不完整，请检查 Nginx 配置"
        fi
    else
        echo "⚠️  Nginx 配置文件不存在，请先运行域名部署脚本"
    fi
}

env_file_security() {
    echo ""
    echo "🔑 检查敏感文件权限..."
    
    ENV_FILE="${PROJECT_DIR}/.env"
    
    if [ -f "${ENV_FILE}" ]; then
        chmod 600 "${ENV_FILE}"
        chown root:root "${ENV_FILE}"
        echo "✅ .env 文件权限已设置为 600 (仅root可读写)"
    fi
    
    if [ -f "${PROJECT_DIR}/db.sqlite3" ]; then
        chmod 640 "${PROJECT_DIR}/db.sqlite3"
        echo "✅ 数据库文件权限已设置为 640"
    fi
}

audit_logging() {
    echo ""
    echo "📊 启用审计日志..."
    
    cat > /etc/audit/rules.d/temu-audit.rules << 'EOF'
-w /opt/temu_tools/.env -p wa -k temu_config
-w /opt/temu_tools/db.sqlite3 -p rw -k temu_database
-a always,exit -F arch=b64 -S execve -k command_monitoring
EOF
    
    systemctl restart auditd 2>/dev/null || true
    echo "✅ 审计日志已启用"
}

create_security_check_script() {
    echo ""
    echo "🔍 创建安全检查脚本..."
    
    cat > ${PROJECT_DIR}/deploy/security_check.sh << 'SECEOF'
#!/bin/bash
echo "=========================================="
echo "  安全状态检查报告"
echo "  $(date)"
echo "=========================================="

echo ""
echo "1. SSL证书状态:"
if command -v certbot &> /dev/null; then
    certbot certificates 2>/dev/null | head -10
else
    echo "   ⚠️ Certbot 未安装"
fi

echo ""
echo "2. 防火墙状态:"
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --list-all | grep -E "ports|services|rich rules"
fi

echo ""
echo "3. SSH安全配置:"
grep -E "^PermitRootLogin|^PasswordAuthentication|^MaxAuthTries" /etc/ssh/sshd_config 2>/dev/null

echo ""
echo "4. Fail2ban状态:"
systemctl is-active fail2ban 2>/dev/null || echo "   ⚠️ 未运行"

echo ""
echo "5. Nginx状态:"
systemctl is-active nginx 2>/dev/null || echo "   ⚠️ 未运行"

echo ""
echo "6. 敏感文件权限:"
ls -la /opt/temu_tools/.env 2>/dev/null || echo "   .env 文件不存在"

echo ""
echo "7. 系统更新状态:"
yum check-update --security 2>/dev/null | head -5 || echo "   无法检查"

echo ""
echo "=========================================="
echo "  检查完成"
echo "=========================================="
SECEOF
    
    chmod +x ${PROJECT_DIR}/deploy/security_check.sh
    echo "✅ 安全检查脚本已创建: deploy/security_check.sh"
}

summary() {
    echo ""
    echo "=========================================="
    echo "  ✅ 企业级安全加固完成！"
    echo "=========================================="
    echo ""
    echo "📋 已完成的加固项:"
    echo "   ✅ SSH安全加固 (禁用密码登录,限制重试次数)"
    echo "   ✅ 系统安全更新"
    echo "   ✅ Fail2ban入侵检测"
    echo "   ✅ 防火墙规则优化"
    echo "   ✅ 日志轮转配置"
    echo "   ✅ 敏感文件权限保护"
    echo "   ✅ 审计日志启用"
    echo "   ✅ 安全头验证"
    echo ""
    echo "🔧 后续操作:"
    echo "   1. 运行安全检查: bash deploy/security_check.sh"
    echo "   2. 定期更新系统: yum update -y"
    echo "   3. 监控日志: tail -f logs/*.log"
    echo "   4. 备份数据库: cp db.sqlite3 backup/db_$(date +%Y%m%d).sqlite3"
    echo ""
    echo "⚠️  重要提醒:"
    echo "   - 请将防火墙规则中的 YOUR_TRUSTED_IP 替换为实际IP"
    echo "   - 确保 SSH密钥已配置好再禁用密码登录"
    echo "   - 定期查看审计日志: ausearch -k temu_config"
    echo ""
}

main() {
    echo "开始执行企业级安全加固..."
    check_root
    secure_ssh
    secure_system
    configure_firewall_rules
    setup_log_rotation
    setup_security_headers
    env_file_security
    audit_logging
    create_security_check_script
    summary
}

main "$@"

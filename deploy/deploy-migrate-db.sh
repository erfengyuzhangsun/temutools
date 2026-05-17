#!/bin/bash
# ===== 阿里云 → DigitalOcean 数据库迁移脚本 =====
#
# 用法（分两步）：
#
# 第1步：在阿里云服务器上导出数据
#   bash deploy/deploy-migrate-db.sh export
#
# 第2步：将 SQL 文件传到 DO 服务器，然后：
#   bash deploy/deploy-migrate-db.sh import /path/to/temu_tools_export.sql
#
# 或直接在两台服务器之间用 SCP 传输：
#   阿里云: bash deploy/deploy-migrate-db.sh export
#   阿里云: scp /tmp/temu_tools_export.sql root@DO_IP:/tmp/
#   DO:     bash deploy/deploy-migrate-db.sh import /tmp/temu_tools_export.sql
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; }

MYSQL_CONTAINER="temu-mysql"
BACKUP_FILE="/tmp/temu_tools_export.sql"
DB_NAME="temu_tools"

# ============================================
# 导出（在阿里云上执行）
# ============================================
do_export() {
    log "========== 阿里云导出数据库 =========="

    # 如果 Docker 在跑，从 Docker MySQL 导出
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "temu-tools-mysql\|temu_mysql\|mysql"; then
        local CONTAINER=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -i mysql | head -1)
        log "从 Docker 容器 $CONTAINER 导出..."

        # 获取 DB 密码
        local DB_PASS=""
        if [ -f /opt/temu_tools_go/.env ]; then
            DB_PASS=$(grep ^DB_PASSWORD= /opt/temu_tools_go/.env | head -1 | cut -d= -f2-)
        elif [ -f /opt/temu_tools/.env ]; then
            DB_PASS=$(grep ^DB_PASSWORD= /opt/temu_tools/.env | head -1 | cut -d= -f2-)
        fi

        if [ -z "$DB_PASS" ]; then
            err "无法从 .env 获取 DB_PASSWORD"
            err "请手动执行: mysqldump -u temu -p temu_tools > $BACKUP_FILE"
            exit 1
        fi

        # Docker 内 mysqldump
        docker exec "$CONTAINER" mysqldump -u temu -p"$DB_PASS" --single-transaction --routines --triggers --databases "$DB_NAME" > "$BACKUP_FILE"

    # 否则从宿主机 MySQL 导出
    elif command -v mysqldump &>/dev/null; then
        log "从宿主机 MySQL 导出..."
        local DB_PASS=""
        if [ -f /opt/temu_tools_go/.env ]; then
            DB_PASS=$(grep ^DB_PASSWORD= /opt/temu_tools_go/.env | head -1 | cut -d= -f2-)
        elif [ -f /opt/temu_tools/.env ]; then
            DB_PASS=$(grep ^DB_PASSWORD= /opt/temu_tools/.env | head -1 | cut -d= -f2-)
        fi
        if [ -n "$DB_PASS" ]; then
            mysqldump -u temu -p"$DB_PASS" --single-transaction --routines --triggers --databases "$DB_NAME" > "$BACKUP_FILE"
        else
            warn "未找到 .env，尝试交互式导出..."
            mysqldump -u root -p --single-transaction --routines --triggers --databases "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null || {
                mysqldump -u temu -p --single-transaction --routines --triggers --databases "$DB_NAME" > "$BACKUP_FILE"
            }
        fi
    else
        err "未找到 mysqldump，请先安装: apt install mysql-client"
        exit 1
    fi

    # 压缩
    gzip -f "$BACKUP_FILE"
    local SIZE=$(ls -lh "${BACKUP_FILE}.gz" | awk '{print $5}')
    log "导出完成: ${BACKUP_FILE}.gz (${SIZE})"

    echo ""
    echo -e "${YELLOW}下一步操作：${NC}"
    echo "  1. 将文件传到 DO 服务器："
    echo "     scp ${BACKUP_FILE}.gz root@你的DO_IP:/tmp/"
    echo ""
    echo "  2. SSH 登录 DO 服务器后导入："
    echo "     bash /opt/temu_tools_go/deploy/deploy-migrate-db.sh import /tmp/temu_tools_export.sql.gz"
    echo ""
}

# ============================================
# 导入（在 DO 上执行）
# ============================================
do_import() {
    local FILE="${1:-$BACKUP_FILE}"
    log "========== DigitalOcean 导入数据库 =========="

    # 解压（如果是 .gz）
    if [[ "$FILE" == *.gz ]]; then
        log "解压 $FILE..."
        gunzip -kf "$FILE"
        FILE="${FILE%.gz}"
    fi

    if [ ! -f "$FILE" ]; then
        err "文件不存在: $FILE"
        exit 1
    fi

    # 等待 MySQL 容器就绪
    if ! docker ps --format '{{.Names}}' | grep -q "^$MYSQL_CONTAINER$"; then
        err "MySQL 容器 $MYSQL_CONTAINER 未运行，请先执行 deploy-do.sh"
        exit 1
    fi

    log "等待 MySQL 就绪..."
    for i in $(seq 1 10); do
        if docker exec "$MYSQL_CONTAINER" mysqladmin ping -u root -p"$DB_PASSWORD" --silent 2>/dev/null; then
            log "MySQL 就绪 ✅"
            break
        fi
        sleep 3
    done

    # 获取 DO 上 .env 中的 DB 密码
    local DO_PASS=""
    if [ -f /opt/temu_tools_go/.env ]; then
        DO_PASS=$(grep ^DB_PASSWORD= /opt/temu_tools_go/.env | head -1 | cut -d= -f2-)
    fi
    if [ -z "$DO_PASS" ]; then
        err "无法获取 DO 上的 DB_PASSWORD"
        exit 1
    fi

    # 导入
    log "导入数据到 $MYSQL_CONTAINER..."
    local TOTAL_LINES=$(wc -l < "$FILE")
    log "SQL 文件: ${TOTAL_LINES} 行"

    # 先清空旧数据（如果有的话），避免冲突
    docker exec -i "$MYSQL_CONTAINER" mysql -u root -p"$DO_PASS" -e "DROP DATABASE IF EXISTS temu_tools; CREATE DATABASE temu_tools CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    docker exec -i "$MYSQL_CONTAINER" mysql -u root -p"$DO_PASS" -e "CREATE USER IF NOT EXISTS 'temu'@'%' IDENTIFIED BY '$DO_PASS'; GRANT ALL PRIVILEGES ON temu_tools.* TO 'temu'@'%'; FLUSH PRIVILEGES;"

    # 导入数据
    docker exec -i "$MYSQL_CONTAINER" mysql -u root -p"$DO_PASS" "$DB_NAME" < "$FILE"

    log "数据导入完成 ✅"

    # 验证
    local TABLE_COUNT=$(docker exec "$MYSQL_CONTAINER" mysql -u root -p"$DO_PASS" -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='temu_tools';" 2>/dev/null)
    log "数据库表数量: $TABLE_COUNT"

    # 验证用户数据
    local USER_COUNT=$(docker exec "$MYSQL_CONTAINER" mysql -u root -p"$DO_PASS" -N -e "SELECT COUNT(*) FROM temu_users;" 2>/dev/null || echo "0")
    log "用户数量: $USER_COUNT"

    rm -f "$FILE"
    log "临时文件已清理"

    echo ""
    echo -e "${GREEN}  🎉 数据迁移完成！${NC}"
    echo -e "  共有 ${TABLE_COUNT} 张表, ${USER_COUNT} 个用户"
    echo -e "  重启 Go 服务使新数据生效: docker compose restart app"
    echo ""
}

# ============================================
# 主入口
# ============================================
case "${1:-}" in
    export)
        do_export
        ;;
    import)
        do_import "${2:-}"
        ;;
    *)
        echo "用法:"
        echo "  导出（阿里云）: bash $0 export"
        echo "  导入（DO）:     bash $0 import <sql文件路径>"
        echo ""
        echo "完整迁移流程:"
        echo "  1. 阿里云: bash $0 export"
        echo "  2. 传输:    scp /tmp/temu_tools_export.sql.gz root@DO_IP:/tmp/"
        echo "  3. DO:      bash $0 import /tmp/temu_tools_export.sql.gz"
        exit 1
        ;;
esac

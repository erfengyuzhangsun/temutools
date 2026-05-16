import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

_table_created = False


def _config():
    import os
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "temu_tools"),
    }


def _connect(dictionary=False):
    import mysql.connector
    c = mysql.connector.connect(**_config())
    return c, c.cursor(dictionary=dictionary) if dictionary else c.cursor()


def execute_mysql(sql: str, params: Tuple = None):
    conn, cur = _connect()
    try:
        cur.execute(sql, params or ())
        conn.commit()
    finally:
        cur.close()
        conn.close()


def query_mysql(sql: str, params: Tuple = None) -> List[Dict]:
    conn, cur = _connect(dictionary=True)
    try:
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


CREATE_SQL = (
    "CREATE TABLE IF NOT EXISTS login_attempts ("
    "attempt_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
    "ip_address VARCHAR(64) NOT NULL, "
    "attempt_time VARCHAR(32) NOT NULL, "
    "password_used VARCHAR(255) DEFAULT '', "
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
)


def ensure_login_attempts_table():
    global _table_created
    if _table_created:
        return
    conn, cur = _connect()
    try:
        cur.execute(CREATE_SQL)
        conn.commit()
        _table_created = True
        logger.info("login_attempts 表已确保存在")
    finally:
        cur.close()
        conn.close()

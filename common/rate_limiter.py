import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5
WINDOW_MINUTES = 15


class LoginRateLimitResult(Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"


def _mask_password(password: str) -> str:
    if not password:
        return ""
    if len(password) <= 4:
        return "*" * len(password)
    return password[:2] + "*" * (len(password) - 4) + password[-2:]


def _ensure_table():
    from common.mysql_direct import ensure_login_attempts_table
    ensure_login_attempts_table()


def get_client_ip() -> str:
    try:
        import streamlit as st
        headers = st.context.headers
        forwarded = headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = headers.get("X-Real-IP", "")
        if real_ip:
            return real_ip.strip()
    except Exception:
        pass
    try:
        import os
        forwarded = os.environ.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    except Exception:
        pass
    return "127.0.0.1"


def _prune_expired_attempts():
    from common.mysql_direct import execute_mysql
    cutoff = (datetime.now() - timedelta(minutes=WINDOW_MINUTES)).isoformat()
    execute_mysql("DELETE FROM login_attempts WHERE attempt_time < %s", (cutoff,))


def check_login_rate_limit(ip_address: str = None) -> LoginRateLimitResult:
    if ip_address is None:
        ip_address = get_client_ip()
    _prune_expired_attempts()
    from common.mysql_direct import query_mysql
    cutoff = (datetime.now() - timedelta(minutes=WINDOW_MINUTES)).isoformat()
    rows = query_mysql(
        "SELECT COUNT(*) as cnt FROM login_attempts "
        "WHERE ip_address = %s AND attempt_time >= %s",
        (ip_address, cutoff),
    )
    count = rows[0]["cnt"] if rows else 0
    if count >= MAX_ATTEMPTS:
        logger.warning(f"登录频率限制触发 | ip={ip_address} | {WINDOW_MINUTES}分钟内失败{count}次")
        return LoginRateLimitResult.BLOCKED
    return LoginRateLimitResult.ALLOWED


def record_login_attempt(ip_address: str = None, password: str = ""):
    if ip_address is None:
        ip_address = get_client_ip()
    masked = _mask_password(password)
    from common.mysql_direct import execute_mysql
    execute_mysql(
        "INSERT INTO login_attempts (ip_address, attempt_time, password_used) "
        "VALUES (%s, %s, %s)",
        (ip_address, datetime.now().isoformat(), masked),
    )


def clear_login_attempts(ip_address: str = None):
    if ip_address is None:
        ip_address = get_client_ip()
    from common.mysql_direct import execute_mysql
    execute_mysql("DELETE FROM login_attempts WHERE ip_address = %s", (ip_address,))

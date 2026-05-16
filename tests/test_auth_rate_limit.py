from datetime import datetime, timedelta


def setup_module():
    from common.mysql_direct import execute_mysql
    execute_mysql("DELETE FROM login_attempts WHERE 1=1")


def test_check_rate_limit_no_attempts():
    from common.rate_limiter import check_login_rate_limit, LoginRateLimitResult
    result = check_login_rate_limit("127.0.0.1")
    assert result == LoginRateLimitResult.ALLOWED, "无历史记录时应允许登录"


def test_check_rate_limit_under_threshold():
    from common.rate_limiter import record_login_attempt, check_login_rate_limit, LoginRateLimitResult
    record_login_attempt("127.0.0.2", "wrong_pwd")
    record_login_attempt("127.0.0.2", "wrong_pwd")
    record_login_attempt("127.0.0.2", "wrong_pwd")
    result = check_login_rate_limit("127.0.0.2")
    assert result == LoginRateLimitResult.ALLOWED, "3次失败应仍允许登录"


def test_check_rate_limit_exceeded():
    from common.rate_limiter import record_login_attempt, check_login_rate_limit, LoginRateLimitResult
    ip = "10.0.0.1"
    record_login_attempt(ip, "wrong_pwd")
    record_login_attempt(ip, "wrong_pwd")
    record_login_attempt(ip, "wrong_pwd")
    record_login_attempt(ip, "wrong_pwd")
    record_login_attempt(ip, "wrong_pwd")
    result = check_login_rate_limit(ip)
    assert result == LoginRateLimitResult.BLOCKED, "5次失败应被阻止登录"


def test_check_rate_limit_clear_on_success():
    from common.rate_limiter import record_login_attempt, check_login_rate_limit, clear_login_attempts, LoginRateLimitResult
    ip = "10.0.0.2"
    record_login_attempt(ip, "wrong_pwd")
    record_login_attempt(ip, "wrong_pwd")
    record_login_attempt(ip, "wrong_pwd")
    clear_login_attempts(ip)
    result = check_login_rate_limit(ip)
    assert result == LoginRateLimitResult.ALLOWED, "清除后应允许登录"


def test_different_ips_independent():
    from common.rate_limiter import record_login_attempt, check_login_rate_limit, LoginRateLimitResult
    ip_a = "10.0.0.3"
    ip_b = "10.0.0.4"
    for _ in range(5):
        record_login_attempt(ip_a, "wrong_pwd")
    assert check_login_rate_limit(ip_a) == LoginRateLimitResult.BLOCKED, "IP_A 5次后应被阻止"
    assert check_login_rate_limit(ip_b) == LoginRateLimitResult.ALLOWED, "IP_B 无记录应允许"


def test_attempts_expire_after_window():
    from common.rate_limiter import check_login_rate_limit, LoginRateLimitResult
    from common.mysql_direct import execute_mysql
    ip = "10.0.0.5"
    execute_mysql(
        "INSERT INTO login_attempts (ip_address, attempt_time) VALUES (%s, %s)",
        (ip, (datetime.now() - timedelta(minutes=20)).isoformat()),
    )
    execute_mysql(
        "INSERT INTO login_attempts (ip_address, attempt_time) VALUES (%s, %s)",
        (ip, (datetime.now() - timedelta(minutes=18)).isoformat()),
    )
    execute_mysql(
        "INSERT INTO login_attempts (ip_address, attempt_time) VALUES (%s, %s)",
        (ip, (datetime.now() - timedelta(minutes=16)).isoformat()),
    )
    execute_mysql(
        "INSERT INTO login_attempts (ip_address, attempt_time) VALUES (%s, %s)",
        (ip, (datetime.now() - timedelta(minutes=14)).isoformat()),
    )
    execute_mysql(
        "INSERT INTO login_attempts (ip_address, attempt_time) VALUES (%s, %s)",
        (ip, (datetime.now() - timedelta(minutes=12)).isoformat()),
    )
    result = check_login_rate_limit(ip)
    assert result == LoginRateLimitResult.ALLOWED, "超时窗外的尝试应被清理，允许登录"


def test_blocked_ip_info():
    from common.rate_limiter import record_login_attempt, check_login_rate_limit, LoginRateLimitResult
    ip = "10.0.0.6"
    for _ in range(5):
        record_login_attempt(ip, "wrong_pwd")
    result = check_login_rate_limit(ip)
    assert result == LoginRateLimitResult.BLOCKED

import logging
import re
from db import execute_query, get_connection, DB_MODE

logger = logging.getLogger(__name__)


def _to_sqlite_safe(sql: str) -> str:
    if DB_MODE == "mysql":
        return sql
    sql = re.sub(r"COMMENT\s*=\s*'[^']*'", "", sql)
    sql = re.sub(r"COMMENT\s+'[^']*'", "", sql)
    sql = re.sub(r"UNIQUE\s+KEY\s+\w+\s*", "UNIQUE ", sql)
    sql = re.sub(r",\s*KEY\s+\w+\s+\([^)]+\)", "", sql)
    replacements = {
        "INTEGER AUTO_INCREMENT PRIMARY KEY": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "DECIMAL(10,2)": "REAL",
        "TINYINT(1)": "INTEGER",
        "VARCHAR(255)": "TEXT",
        "VARCHAR(100)": "TEXT",
        "VARCHAR(50)": "TEXT",
        "VARCHAR(30)": "TEXT",
        "VARCHAR(20)": "TEXT",
        "ENGINE=InnoDB": "",
        "DEFAULT CHARSET=utf8mb4": "",
        "ON UPDATE CURRENT_TIMESTAMP": "",
    }
    for old, new in replacements.items():
        sql = sql.replace(old, new)
    return sql


SCHEDULER_TABLES = {
    "temu_scheduler_tasks": """
        CREATE TABLE IF NOT EXISTS temu_scheduler_tasks (
            task_id VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL COMMENT '任务名称',
            cron_expression VARCHAR(50) NOT NULL COMMENT 'Cron表达式',
            timeout_seconds INT DEFAULT 300 COMMENT '超时时间',
            max_retries INT DEFAULT 3 COMMENT '最大重试',
            enabled TINYINT(1) DEFAULT 1 COMMENT '是否启用',
            description TEXT DEFAULT NULL COMMENT '描述',
            last_run_at TIMESTAMP NULL DEFAULT NULL COMMENT '上次执行',
            next_run_at TIMESTAMP NULL DEFAULT NULL COMMENT '下次执行',
            run_count INT DEFAULT 0 COMMENT '执行次数',
            fail_count INT DEFAULT 0 COMMENT '失败次数',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='定时任务定义';
    """,
    "temu_scheduler_logs": """
        CREATE TABLE IF NOT EXISTS temu_scheduler_logs (
            log_id INTEGER AUTO_INCREMENT PRIMARY KEY,
            task_id VARCHAR(100) NOT NULL COMMENT '任务ID',
            status VARCHAR(20) NOT NULL COMMENT '状态',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
            finished_at TIMESTAMP NULL DEFAULT NULL COMMENT '结束时间',
            duration_seconds DECIMAL(10,2) DEFAULT 0.00 COMMENT '耗时',
            error_message TEXT DEFAULT NULL COMMENT '错误信息',
            retry_count INT DEFAULT 0 COMMENT '重试次数'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务执行日志';
    """,
}


def initialize_scheduler_tables():
    for table_name, sql in SCHEDULER_TABLES.items():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            safe_sql = _to_sqlite_safe(sql)
            cursor.execute(safe_sql)
            cursor.close()
            conn.commit()
            conn.close()
            logger.info(f"数据表创建成功: {table_name}")
        except Exception as e:
            logger.error(f"创建表 {table_name} 失败: {e}")

import os
import logging
from datetime import datetime
from typing import Optional

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"temu_{datetime.now().strftime('%Y%m')}.log")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            from db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            log_entry = self.format(record)
            user_id = getattr(record, 'user_id', None)
            if user_id:
                cursor.execute(
                    "INSERT INTO system_logs (user_id, level, message) VALUES (?, ?, ?)",
                    (user_id, record.levelname, log_entry)
                )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            pass


def setup_logger(name: str = "temu_tools") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    if not logger.handlers:
        os.makedirs(LOG_DIR, exist_ok=True)

        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-5s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger()


def log_action(action: str, user_id: Optional[int] = None, details: str = ""):
    msg = f"[用户 {user_id}] {action}" if user_id else action
    if details:
        msg += f" | {details}"
    logger.info(msg)


def log_error(error: str, user_id: Optional[int] = None):
    msg = f"[用户 {user_id}] 错误: {error}" if user_id else f"错误: {error}"
    logger.error(msg)


def log_warning(warning: str, user_id: Optional[int] = None):
    msg = f"[用户 {user_id}] 警告: {warning}" if user_id else f"警告: {warning}"
    logger.warning(msg)

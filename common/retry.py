import asyncio
import logging
from functools import wraps
from typing import Callable, Optional, Type, Tuple

logger = logging.getLogger(__name__)


class RetryConfig:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 5.0,
        max_delay: float = 120.0,
        backoff_factor: float = 2.0,
        retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retryable_exceptions = retryable_exceptions or (ConnectionError, TimeoutError, IOError)


def async_retry(config: RetryConfig = None):
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_retries:
                        delay = min(config.base_delay * (config.backoff_factor ** (attempt - 1)), config.max_delay)
                        logger.warning(
                            f"{func.__name__} 第{attempt}次重试 | 等待{delay:.1f}s | 错误: {e}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} 重试{config.max_retries}次均失败 | 最后错误: {e}"
                        )
            raise last_exception
        return wrapper
    return decorator


def sync_retry(config: RetryConfig = None):
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            for attempt in range(1, config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_retries:
                        delay = min(config.base_delay * (config.backoff_factor ** (attempt - 1)), config.max_delay)
                        logger.warning(
                            f"{func.__name__} 第{attempt}次重试 | 等待{delay:.1f}s | 错误: {e}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} 重试{config.max_retries}次均失败 | 最后错误: {e}"
                        )
            raise last_exception
        return wrapper
    return decorator

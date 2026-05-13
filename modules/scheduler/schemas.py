from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, Awaitable, Any
from enum import Enum


class TaskStatus(str, Enum):
    REGISTERED = "registered"
    RUNNING = "running"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TaskDefinition:
    task_id: str
    name: str
    cron_expression: str
    callback: Callable[[], Awaitable[None]]
    timeout_seconds: int = 300
    max_retries: int = 3
    enabled: bool = True
    description: str = ""


@dataclass
class TaskData:
    definition: TaskDefinition
    status: TaskStatus = TaskStatus.REGISTERED
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    fail_count: int = 0


@dataclass
class TaskStatusInfo:
    task_id: str
    name: str
    status: TaskStatus
    cron_expression: str
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    fail_count: int = 0
    enabled: bool = True


@dataclass
class TaskLog:
    log_id: int
    task_id: str
    status: TaskStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_message: str = ""
    retry_count: int = 0


@dataclass
class TaskResult:
    success: bool
    message: str = ""
    duration_seconds: float = 0.0
    retry_count: int = 0


@dataclass
class ServiceResult:
    success: bool
    message: str = ""
    data: Any = None
    error_code: str = ""

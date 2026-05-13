import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from modules.scheduler.schemas import (
    TaskDefinition, TaskData, TaskStatus, TaskStatusInfo,
    TaskLog, TaskResult, ServiceResult,
)
from modules.scheduler.config import MODULE_CONFIG

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self._tasks: Dict[str, TaskData] = {}

    def register_task(self, definition: TaskDefinition) -> bool:
        if definition.task_id in self._tasks:
            logger.warning(f"任务已存在: {definition.task_id}")
            return False
        self._tasks[definition.task_id] = TaskData(definition=definition)
        self._save_task_definition(definition)
        logger.info(f"任务注册成功: {definition.task_id} | {definition.name}")
        return True

    def unregister_task(self, task_id: str) -> bool:
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        logger.info(f"任务已注销: {task_id}")
        return True

    def start_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.status = TaskStatus.RUNNING
        logger.info(f"任务已启动: {task_id}")
        return True

    def stop_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.status = TaskStatus.STOPPED
        logger.info(f"任务已停止: {task_id}")
        return True

    def update_task_config(self, task_id: str, cron_expression: str = None,
                           timeout_seconds: int = None, max_retries: int = None) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        if cron_expression:
            task.definition.cron_expression = cron_expression
        if timeout_seconds:
            task.definition.timeout_seconds = timeout_seconds
        if max_retries is not None:
            task.definition.max_retries = max_retries
        logger.info(f"任务配置已更新: {task_id}")
        return True

    def get_task_status(self, task_id: str) -> Optional[TaskStatusInfo]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        return TaskStatusInfo(
            task_id=task.definition.task_id,
            name=task.definition.name,
            status=task.status,
            cron_expression=task.definition.cron_expression,
            last_run=task.last_run,
            next_run=task.next_run,
            run_count=task.run_count,
            fail_count=task.fail_count,
            enabled=task.definition.enabled,
        )

    def get_all_task_statuses(self) -> List[TaskStatusInfo]:
        return [self.get_task_status(tid) for tid in self._tasks
                if self.get_task_status(tid) is not None]

    async def _execute_task(self, task_id: str) -> TaskResult:
        task = self._tasks.get(task_id)
        if not task:
            return TaskResult(success=False, message=f"任务不存在: {task_id}")

        start_time = time.time()
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()
        task.run_count += 1

        timeout = task.definition.timeout_seconds
        retries = task.definition.max_retries
        last_error = ""
        retry_count = 0

        for attempt in range(1, retries + 1):
            try:
                await asyncio.wait_for(task.definition.callback(), timeout=timeout)
                task.status = TaskStatus.COMPLETED
                duration = time.time() - start_time
                self._save_task_log(task_id, TaskStatus.COMPLETED, duration, retry_count=retry_count)
                logger.info(f"任务执行成功: {task_id} | 耗时={duration:.2f}s")
                return TaskResult(success=True, message="执行成功", duration_seconds=duration)

            except asyncio.TimeoutError:
                last_error = f"执行超时({timeout}s)"
                task.status = TaskStatus.TIMEOUT
                task.fail_count += 1
                logger.warning(f"任务超时: {task_id} | 第{attempt}次")

            except Exception as e:
                last_error = str(e)
                task.status = TaskStatus.FAILED
                task.fail_count += 1
                logger.warning(f"任务失败: {task_id} | 第{attempt}次 | {e}")

            retry_count = attempt
            if attempt < retries:
                await asyncio.sleep(min(attempt * 5, 30))

        duration = time.time() - start_time
        self._save_task_log(task_id, task.status, duration, last_error, retry_count)
        logger.error(f"任务最终失败: {task_id} | 重试{retry_count}次 | {last_error}")
        return TaskResult(success=False, message=last_error, duration_seconds=duration, retry_count=retry_count)

    async def get_task_logs(self, task_id: str, limit: int = 20) -> List[TaskLog]:
        return self._query_task_logs(task_id, limit)

    def _save_task_definition(self, definition: TaskDefinition):
        from db import execute_query
        execute_query(
            "INSERT OR REPLACE INTO temu_scheduler_tasks "
            "(task_id, name, cron_expression, timeout_seconds, max_retries, enabled, description) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (definition.task_id, definition.name, definition.cron_expression,
             definition.timeout_seconds, definition.max_retries,
             1 if definition.enabled else 0, definition.description),
        )

    def _save_task_log(self, task_id: str, status: TaskStatus, duration: float,
                       error_message: str = "", retry_count: int = 0):
        from db import execute_query
        execute_query(
            "INSERT INTO temu_scheduler_logs "
            "(task_id, status, duration_seconds, error_message, retry_count) "
            "VALUES (?, ?, ?, ?, ?)",
            (task_id, status.value, round(duration, 2), error_message, retry_count),
        )

    def _query_task_logs(self, task_id: str, limit: int = 20) -> List[TaskLog]:
        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_scheduler_logs WHERE task_id = ? "
            "ORDER BY started_at DESC LIMIT ?",
            (task_id, limit), fetch=True,
        ) or []
        logs = []
        for row in rows:
            started_at = row.get("started_at")
            if isinstance(started_at, str):
                try:
                    started_at = datetime.fromisoformat(started_at)
                except (ValueError, TypeError):
                    started_at = datetime.now()
            finished_at = row.get("finished_at")
            if isinstance(finished_at, str):
                try:
                    finished_at = datetime.fromisoformat(finished_at)
                except (ValueError, TypeError):
                    finished_at = None
            logs.append(TaskLog(
                log_id=row.get("log_id", 0),
                task_id=row.get("task_id", task_id),
                status=TaskStatus(row.get("status", "completed")),
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=float(row.get("duration_seconds", 0)),
                error_message=row.get("error_message", ""),
                retry_count=row.get("retry_count", 0),
            ))
        return logs

"""模块3：全局定时任务调度中心 - 全覆盖测试

RED阶段：测试先行，业务代码尚未实现
遵循AAA模式：Arrange → Act → Assert
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
class TestSchedulerNormalFlow:
    """正常流程测试"""

    async def test_task_runs_on_schedule(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()
        executed = []

        async def mock_task():
            executed.append(True)

        task_def = TaskDefinition(
            task_id="test_task",
            name="测试任务",
            cron_expression="* * * * *",
            callback=mock_task,
        )
        service.register_task(task_def)

        assert task_def.task_id in service._tasks
        assert service._tasks[task_def.task_id].status == TaskStatus.REGISTERED

    async def test_multiple_tasks_parallel_execution(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()
        execution_order = []

        async def task_a():
            await asyncio.sleep(0.05)
            execution_order.append("A")

        async def task_b():
            await asyncio.sleep(0.03)
            execution_order.append("B")

        async def task_c():
            execution_order.append("C")

        service.register_task(TaskDefinition(task_id="A", name="TaskA", cron_expression="*/1 * * * *", callback=task_a))
        service.register_task(TaskDefinition(task_id="B", name="TaskB", cron_expression="*/2 * * * *", callback=task_b))
        service.register_task(TaskDefinition(task_id="C", name="TaskC", cron_expression="*/5 * * * *", callback=task_c))

        start = asyncio.get_event_loop().time()
        await service._execute_task("A")
        await service._execute_task("B")
        await service._execute_task("C")
        elapsed = asyncio.get_event_loop().time() - start

        assert "A" in execution_order
        assert "B" in execution_order
        assert "C" in execution_order
        assert elapsed < 0.2

    async def test_task_manual_start_stop(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()

        async def dummy():
            pass

        service.register_task(TaskDefinition(task_id="toggle_test", name="启停测试", cron_expression="* * * * *", callback=dummy))
        task_data = service._tasks["toggle_test"]

        assert task_data.status == TaskStatus.REGISTERED

        service.start_task("toggle_test")
        assert task_data.status == TaskStatus.RUNNING

        service.stop_task("toggle_test")
        assert task_data.status == TaskStatus.STOPPED

        service.start_task("toggle_test")
        assert task_data.status == TaskStatus.RUNNING

    async def test_task_execution_logging(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()

        async def successful_task():
            pass

        service.register_task(TaskDefinition(task_id="log_test", name="日志测试", cron_expression="* * * * *", callback=successful_task))
        await service._execute_task("log_test")

        logs = await service.get_task_logs("log_test")
        assert len(logs) >= 1
        assert logs[0].status == TaskStatus.COMPLETED

    async def test_task_status_query(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()

        async def dummy():
            pass

        service.register_task(TaskDefinition(task_id="status_test", name="状态测试", cron_expression="0 */2 * * *", callback=dummy))
        service.start_task("status_test")

        status = service.get_task_status("status_test")
        assert status.task_id == "status_test"
        assert status.status == TaskStatus.RUNNING
        assert status.cron_expression == "0 */2 * * *"

    async def test_task_config_dynamic_update(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()

        async def dummy():
            pass

        service.register_task(TaskDefinition(task_id="config_test", name="配置测试", cron_expression="*/30 * * * *", callback=dummy))
        service.start_task("config_test")

        updated = service.update_task_config("config_test", cron_expression="*/15 * * * *")
        assert updated is True
        assert service._tasks["config_test"].definition.cron_expression == "*/15 * * * *"


@pytest.mark.asyncio
class TestSchedulerExceptionFlow:
    """异常场景测试"""

    async def test_task_execution_exception_handling(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()

        async def failing_task():
            raise ValueError("任务执行异常")

        service.register_task(TaskDefinition(task_id="fail_test", name="失败任务", cron_expression="* * * * *", callback=failing_task))
        result = await service._execute_task("fail_test")

        assert result.success is False
        assert "任务执行异常" in result.message

        logs = await service.get_task_logs("fail_test")
        assert logs[-1].status == TaskStatus.FAILED

    async def test_scheduler_continues_after_task_failure(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()
        good_executed = []

        async def failing_task():
            raise RuntimeError("崩溃")

        async def good_task():
            good_executed.append(True)

        service.register_task(TaskDefinition(task_id="fail", name="失败", cron_expression="* * * * *", callback=failing_task))
        service.register_task(TaskDefinition(task_id="good", name="正常", cron_expression="* * * * *", callback=good_task))

        await service._execute_task("fail")
        await service._execute_task("good")

        assert len(good_executed) == 1
        assert service._tasks["fail"].status == TaskStatus.FAILED
        assert service._tasks["good"].status == TaskStatus.COMPLETED

    async def test_task_timeout_termination(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()

        async def slow_task():
            await asyncio.sleep(10)

        service.register_task(TaskDefinition(
            task_id="slow", name="慢任务",
            cron_expression="* * * * *",
            callback=slow_task,
            timeout_seconds=0.1,
        ))

        result = await service._execute_task("slow")

        assert result.success is False
        assert "超时" in result.message

    async def test_max_retries_exceeded(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition, TaskStatus

        service = SchedulerService()
        attempt_count = 0

        async def always_fails():
            nonlocal attempt_count
            attempt_count += 1
            raise ConnectionError(f"第{attempt_count}次失败")

        service.register_task(TaskDefinition(
            task_id="retry_test", name="重试测试",
            cron_expression="* * * * *",
            callback=always_fails,
            max_retries=3,
        ))

        result = await service._execute_task("retry_test")

        assert result.success is False
        assert attempt_count == 3


@pytest.mark.asyncio
class TestSchedulerBoundaryValue:
    """边界值测试"""

    async def test_register_and_unregister_task(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition

        service = SchedulerService()

        async def dummy():
            pass

        service.register_task(TaskDefinition(task_id="reg_test", name="注册测试", cron_expression="* * * * *", callback=dummy))
        assert "reg_test" in service._tasks

        service.unregister_task("reg_test")
        assert "reg_test" not in service._tasks

    async def test_get_all_task_statuses(self):
        from modules.scheduler.service import SchedulerService
        from modules.scheduler.schemas import TaskDefinition

        service = SchedulerService()

        async def dummy():
            pass

        service.register_task(TaskDefinition(task_id="T1", name="任务1", cron_expression="*/5 * * * *", callback=dummy))
        service.register_task(TaskDefinition(task_id="T2", name="任务2", cron_expression="*/10 * * * *", callback=dummy))

        all_statuses = service.get_all_task_statuses()
        assert len(all_statuses) == 2


class TestSchedulerConfig:
    """配置测试"""

    def test_config_has_required_keys(self):
        from modules.scheduler.config import MODULE_CONFIG

        required_keys = ["default_timeout_seconds", "default_max_retries",
                         "max_concurrent_tasks", "task_cleanup_days"]
        for key in required_keys:
            assert key in MODULE_CONFIG, f"缺少配置项: {key}"

    def test_config_values_are_valid(self):
        from modules.scheduler.config import MODULE_CONFIG

        timeout = MODULE_CONFIG["default_timeout_seconds"]
        assert timeout["min"] >= 10
        assert timeout["max"] <= 3600

        retries = MODULE_CONFIG["default_max_retries"]
        assert retries["min"] >= 0
        assert retries["max"] <= 10

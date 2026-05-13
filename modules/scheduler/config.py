MODULE_CONFIG = {
    "default_timeout_seconds": {
        "default": 300,
        "min": 10,
        "max": 3600,
        "type": "int",
        "description": "任务默认超时时间(秒)",
    },
    "default_max_retries": {
        "default": 3,
        "min": 0,
        "max": 10,
        "type": "int",
        "description": "任务默认最大重试次数",
    },
    "max_concurrent_tasks": {
        "default": 10,
        "min": 1,
        "max": 100,
        "type": "int",
        "description": "最大并发任务数",
    },
    "task_cleanup_days": {
        "default": 30,
        "min": 1,
        "max": 365,
        "type": "int",
        "description": "任务日志保留天数",
    },
    "scheduler_enabled": {
        "default": True,
        "type": "bool",
        "description": "是否启用调度中心",
    },
}

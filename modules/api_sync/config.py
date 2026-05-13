MODULE_CONFIG = {
    "sync_interval_minutes": {
        "default": 60,
        "min": 5,
        "max": 1440,
        "type": "int",
        "description": "自动同步间隔（分钟）",
    },
    "max_retry_count": {
        "default": 3,
        "min": 0,
        "max": 10,
        "type": "int",
        "description": "最大重试次数",
    },
    "retry_interval_seconds": {
        "default": 30,
        "min": 5,
        "max": 600,
        "type": "int",
        "description": "重试间隔（秒）",
    },
    "page_size": {
        "default": 500,
        "min": 10,
        "max": 1000,
        "type": "int",
        "description": "API分页大小",
    },
    "sync_enabled": {
        "default": True,
        "type": "bool",
        "description": "是否启用自动同步",
    },
    "auto_retry_enabled": {
        "default": True,
        "type": "bool",
        "description": "失败是否自动重试",
    },
}

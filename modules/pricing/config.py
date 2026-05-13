MODULE_CONFIG = {
    "default_profit_threshold": {
        "default": 20.0,
        "min": 1.0,
        "max": 100.0,
        "type": "float",
        "description": "默认毛利率阈值(%)",
    },
    "activity_profit_threshold": {
        "default": 10.0,
        "min": 0.0,
        "max": 50.0,
        "type": "float",
        "description": "活动商品毛利率阈值(%)",
    },
    "expiry_reminder_hours": {
        "default": 2,
        "min": 1,
        "max": 72,
        "type": "int",
        "description": "核价超时前N小时提醒",
    },
    "max_notices_per_page": {
        "default": 50,
        "min": 10,
        "max": 200,
        "type": "int",
        "description": "每页获取核价通知数量",
    },
    "auto_handle_enabled": {
        "default": True,
        "type": "bool",
        "description": "是否启用自动核价处理",
    },
}

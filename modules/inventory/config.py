MODULE_CONFIG = {
    "safety_stock_days": {"default": 7, "min": 1, "max": 90, "type": "int", "description": "安全库存天数"},
    "slow_moving_days": {"default": 30, "min": 7, "max": 180, "type": "int", "description": "滞销判定天数"},
    "auto_sync_interval": {"default": 60, "min": 5, "max": 1440, "type": "int", "description": "库存自动同步间隔(分钟)"},
    "low_stock_warning_threshold": {"default": 20, "min": 1, "max": 10000, "type": "int", "description": "低库存告警阈值(件)"},
    "replenishment_lead_time_default": {"default": 7, "min": 1, "max": 60, "type": "int", "description": "默认采购提前期(天)"},
}

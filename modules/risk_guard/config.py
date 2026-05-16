MODULE_CONFIG = {
    "min_safe_margin": {
        "default": 10.0,
        "min": 3.0,
        "max": 30.0,
        "type": "float",
        "description": "最低安全毛利率(%)",
    },
    "max_single_change_percent": {
        "default": 5.0,
        "min": 1.0,
        "max": 20.0,
        "type": "float",
        "description": "单次最大调价幅度(%)",
    },
    "max_frequent_adjustments_24h": {
        "default": 3,
        "min": 1,
        "max": 10,
        "type": "int",
        "description": "24小时内最大调价次数",
    },
    "max_increase_percent": {
        "default": 10.0,
        "min": 1.0,
        "max": 30.0,
        "type": "float",
        "description": "最大安全涨价幅度(%)",
    },
}

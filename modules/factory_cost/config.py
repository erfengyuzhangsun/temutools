MODULE_CONFIG = {
    "default_expected_margin": {
        "default": 20.0,
        "min": 1.0,
        "max": 100.0,
        "type": "float",
        "description": "默认期望毛利率(%)",
    },
    "full_commission_min_margin": {
        "default": 15.0,
        "min": 5.0,
        "max": 50.0,
        "type": "float",
        "description": "全托管最低保本毛利率(%)",
    },
    "half_commission_min_margin": {
        "default": 10.0,
        "min": 3.0,
        "max": 40.0,
        "type": "float",
        "description": "半托管最低保本毛利率(%)",
    },
    "safe_price_floor_ratio": {
        "default": 0.85,
        "min": 0.5,
        "max": 1.0,
        "type": "float",
        "description": "安全供货价下限系数(相对建议价)",
    },
    "safe_price_ceiling_ratio": {
        "default": 1.15,
        "min": 1.0,
        "max": 2.0,
        "type": "float",
        "description": "安全供货价上限系数(相对建议价)",
    },
    "max_images_per_product": {
        "default": 9,
        "min": 1,
        "max": 20,
        "type": "int",
        "description": "每个商品最大图片数",
    },
}

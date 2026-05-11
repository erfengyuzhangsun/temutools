CATEGORY_COMMISSION_RATES = {
    "家居百货": 0.08,
    "3C数码": 0.11,
    "服装鞋包": 0.10,
    "美妆个护": 0.09,
    "玩具母婴": 0.07,
    "食品饮料": 0.05,
}

PERFORMANCE_FEES = {
    "excellent": {"min_score": 4.8, "rate": 0.00, "label": "优秀"},
    "good": {"min_score": 4.5, "rate": 0.02, "label": "良好"},
    "average": {"min_score": 4.2, "rate": 0.05, "label": "一般"},
    "poor": {"min_score": 0, "rate": 0.10, "label": "较差"},
}

PAYMENT_PROCESSING_RATE = 0.0175
PAYMENT_PROCESSING_FIXED = 0.85

RETURN_RESIDUAL_VALUE = 0.20
SHIPPING_PENALTY_RATE = 0.05

CSV_FIELD_MAPPING = {
    "订单号": ["order_id", "订单号", "Order ID", "order_no"],
    "SKU": ["sku", "SKU", "商品编码", "Product SKU"],
    "商品名称": ["product_name", "商品名称", "Product Name", "商品标题"],
    "买家支付金额": ["buyer_payment", "买家支付金额", "Buyer Payment", "实收金额"],
    "平台运费": ["platform_shipping", "平台运费", "Platform Shipping", "运费"],
    "结算价": ["settlement_price", "结算价", "Settlement Price", "供货价"],
    "类目": ["category", "类目", "Category", "商品类目"],
    "发货时间": ["ship_time", "发货时间", "Ship Time", "发货日期"],
    "确认收货时间": ["confirm_time", "确认收货时间", "Confirm Time", "完成时间"],
    "退货状态": ["return_status", "退货状态", "Return Status", "是否退货"],
    "成本价": ["cost_price", "成本价", "Cost Price", "采购价"],
    "店铺评分": ["store_score", "店铺评分", "Store Score", "综合评分"]
}

DEFAULT_STORE_SCORE = 4.8
PROFIT_WARNING_THRESHOLD = 5.0

RISK_THRESHOLDS = {
    "shipping_timeout": {
        "name": "发货超时率",
        "safe": 0.04,
        "warning": 0.045,
        "danger": 0.05,
        "penalty": "每单罚 5-10 元",
        "unit": "%"
    },
    "fake_shipping": {
        "name": "虚假发货率",
        "safe": 0.001,
        "warning": 0.003,
        "danger": 0.005,
        "penalty": "每单罚 50-100 元",
        "unit": "%"
    },
    "product_mismatch": {
        "name": "货不对版率",
        "safe": 0.005,
        "warning": 0.01,
        "danger": 0.02,
        "penalty": "罚销售额 10 倍",
        "unit": "%"
    },
    "stockout_rate": {
        "name": "缺货率",
        "safe": 0.01,
        "warning": 0.02,
        "danger": 0.03,
        "penalty": "罚货值 5 倍",
        "unit": "%"
    },
    "return_rate": {
        "name": "退货率",
        "safe": 0.12,
        "warning": 0.14,
        "danger": 0.15,
        "penalty": "强制下架",
        "unit": "%"
    },
    "negative_review_rate": {
        "name": "差评率",
        "safe": 0.02,
        "warning": 0.025,
        "danger": 0.03,
        "penalty": "降权限流",
        "unit": "%"
    }
}

PRICING_PLANS = {
    "basic": {
        "name": "基础版",
        "price_monthly": 29.9,
        "features": ["利润计算", "CSV 导入", "基础风险预警"]
    },
    "pro": {
        "name": "专业版",
        "price_monthly": 39.9,
        "features": ["API 自动同步", "实时亏损预警", "90 天回款预测", "完整罚款监控"]
    },
    "lifetime": {
        "name": "终身版",
        "price": 399,
        "features": ["所有功能", "永久更新", "专属社群"]
    }
}

MODULE_CONFIG={
    "min_gross_margin":{"default":15.0,"min":0.0,"max":100.0,"type":"float","description":"最低保本毛利率(%)"},
    "max_daily_adjustments":{"default":5,"min":1,"max":50,"type":"int","description":"每日最大调价次数"},
    "competitor_price_drop_ratio":{"default":0.5,"min":0.0,"max":1.0,"type":"float","description":"竞品降价跟进比例"},
    "price_adjustment_cooldown_hours":{"default":24,"min":1,"max":168,"type":"int","description":"调价冷却时间(小时)"},
}

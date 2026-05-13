MODULE_CONFIG={
    "auto_sync_settlement":{"default":True,"type":"bool","description":"自动同步结算账单"},
    "payout_prediction_deviation":{"default":5.0,"type":"float","description":"回款预估偏差(%)"},
    "reconciliation_threshold":{"default":0.5,"min":0.0,"max":100,"type":"float","description":"对账差异告警阈值(元)"},
}

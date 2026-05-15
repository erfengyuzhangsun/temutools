MODULE_CONFIG={
  "cpu_threshold":{"default":80.0,"min":50.0,"max":99.0,"type":"float","description":"CPU使用率告警阈值(%)"},
  "cpu_critical_threshold":{"default":95.0,"min":90.0,"max":100.0,"type":"float","description":"CPU严重告警阈值(%)"},
  "memory_threshold":{"default":85.0,"min":60.0,"max":99.0,"type":"float","description":"内存使用率告警阈值(%)"},
  "memory_critical_mb":{"default":200,"min":50,"max":1024,"type":"int","description":"内存严重不足告警线(MB)"},
  "disk_threshold":{"default":90.0,"min":70.0,"max":99.0,"type":"float","description":"磁盘使用率告警阈值(%)"},
  "disk_critical_threshold":{"default":98.0,"min":95.0,"max":100.0,"type":"float","description":"磁盘严重告警阈值(%)"},
  "check_interval":{"default":30,"min":10,"max":300,"type":"int","description":"检查间隔(秒)"},
  "alert_cooldown_seconds":{"default":300,"min":60,"max":3600,"type":"int","description":"同类告警冷却时间(秒)"},
  "alert_ttl_seconds":{"default":3600,"min":600,"max":86400,"type":"int","description":"告警保留时间(秒)"},
  "notification_webhook":{"default":None,"type":"string","description":"告警通知Webhook URL"},
  "health_score_weights":{
    "cpu":{"default":0.3,"min":0.1,"max":0.5,"type":"float","description":"CPU权重"},
    "memory":{"default":0.3,"min":0.1,"max":0.5,"type":"float","description":"内存权重"},
    "disk":{"default":0.2,"min":0.1,"max":0.4,"type":"float","description":"磁盘权重"},
    "processes":{"default":0.2,"min":0.0,"max":0.4,"type":"float","description":"进程权重"}
  }
}

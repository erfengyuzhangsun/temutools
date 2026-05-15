from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AlertSchema(BaseModel):
    type: str = Field(..., description="告警类型: cpu/memory/disk/process")
    level: str = Field(..., description="告警级别: critical/warning/info")
    message: str = Field(..., description="告警消息")
    metric_value: float = Field(..., description="当前指标值")
    threshold: float = Field(..., description="告警阈值")
    timestamp: datetime = Field(default_factory=datetime.now, description="告警时间")
    acknowledged: bool = Field(default=False, description="是否已确认")

class ServerHealthSchema(BaseModel):
    status: str = Field(..., description="整体状态: healthy/degraded/warning/critical")
    health_score: float = Field(..., description="健康评分(0-100)")
    cpu_usage: Optional[float] = Field(None, description="CPU使用率")
    memory_usage: Optional[float] = Field(None, description="内存使用率")
    disk_usage: Optional[float] = Field(None, description="磁盘使用率")
    alert_count: int = Field(default=0, description="活跃告警数")
    last_check: datetime = Field(default_factory=datetime.now, description="最后检查时间")

class MonitorConfigSchema(BaseModel):
    cpu_threshold: float = Field(default=80.0, ge=50.0, le=99.0)
    cpu_critical_threshold: float = Field(default=95.0, ge=90.0, le=100.0)
    memory_threshold: float = Field(default=85.0, ge=60.0, le=99.0)
    disk_threshold: float = Field(default=90.0, ge=70.0, le=99.0)
    check_interval: int = Field(default=30, ge=10, le=300)
    alert_cooldown_seconds: int = Field(default=300, ge=60, le=3600)
    notification_webhook: Optional[str] = Field(None, description="Webhook URL")

class ServiceResult(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from enum import Enum


class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class SyncType(str, Enum):
    ORDER = "order"
    INVENTORY = "inventory"
    PRICING = "pricing"
    SETTLEMENT = "settlement"
    METRICS = "metrics"
    ACTIVITY = "activity"
    MESSAGE = "message"


@dataclass
class ServiceResult:
    success: bool
    message: str = ""
    data: Any = None
    error_code: str = ""


@dataclass
class SyncResult(ServiceResult):
    sync_status: SyncStatus = SyncStatus.PENDING
    synced_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    def __post_init__(self):
        if self.synced_at is None:
            self.synced_at = datetime.now()


@dataclass
class SyncRecord:
    order_id: str
    sku: str
    product_name: str
    category: str
    buyer_payment: float
    platform_shipping: float
    settlement_price: float
    cost_price: float
    status: str
    create_time: Optional[str] = None
    ship_time: Optional[str] = None
    confirm_time: Optional[str] = None
    return_status: str = ""
    store_score: float = 4.8
    quantity: int = 1


@dataclass
class SyncHistoryItem:
    sync_id: int
    shop_id: int
    sync_type: str
    status: SyncStatus
    synced_count: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_message: str = ""
    record_count: int = 0


@dataclass
class ShopBindRequest:
    shop_name: str
    api_key: str
    api_secret: str
    main_category: str = "家居百货"


@dataclass
class ShopInfo:
    shop_id: int
    shop_name: str
    main_category: str
    is_active: bool = True
    last_sync_time: Optional[datetime] = None
    created_at: Optional[datetime] = None

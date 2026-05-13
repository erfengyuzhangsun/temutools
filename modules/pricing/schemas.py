from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from enum import Enum


class PricingAction(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    SKIP = "skip"


@dataclass
class PricingResult:
    notice_id: str
    sku: str
    supply_price: float
    cost_price: float
    gross_margin: float
    action: PricingAction
    reason: str = ""


@dataclass
class PricingLogItem:
    log_id: int
    notice_id: str
    sku: str
    action: str
    supply_price: float
    cost_price: float
    gross_margin: float
    handled_at: datetime
    reason: str = ""
    is_activity: bool = False


@dataclass
class ServiceResult:
    success: bool
    message: str = ""
    data: Any = None
    error_code: str = ""

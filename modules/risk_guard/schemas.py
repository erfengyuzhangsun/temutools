from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class RiskRule:
    rule_id: str
    name: str
    description: str
    severity: str
    condition_desc: str


@dataclass
class PricingCheckResult:
    sku_code: str
    product_name: str
    current_supply_price: float
    new_supply_price: float
    change_percent: float
    passed: bool
    triggered_rules: List[str]
    risk_level: str
    advice: str
    checked_at: str


@dataclass
class RiskHistory:
    history_id: int = 0
    sku_code: str = ""
    operation: str = ""
    detail: str = ""
    risk_level: str = ""
    created_at: str = ""

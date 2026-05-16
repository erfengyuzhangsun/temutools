from dataclasses import dataclass
from typing import Optional


@dataclass
class CostBreakdown:
    material_cost: float
    labor_cost: float
    packaging_cost: float
    shipping_cost: float
    other_cost: float
    total_cost: float


@dataclass
class PriceSuggestion:
    sku_code: str
    product_name: str
    cost_breakdown: CostBreakdown
    mode: str
    suggested_supply_price: float
    platform_sale_price: Optional[float]
    commission_amount: float
    shipping_subsidy: float
    net_profit: float
    net_profit_margin: float
    min_acceptable_price: float
    max_safe_price: float
    risk_level: str
    warnings: list


@dataclass
class AdjustmentRecord:
    adj_id: int = 0
    sku_code: str = ""
    old_price: float = 0.0
    new_price: float = 0.0
    change_percent: float = 0.0
    reason: str = ""
    created_at: str = ""

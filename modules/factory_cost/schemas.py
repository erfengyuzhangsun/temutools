from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ProductInfo:
    product_id: int = 0
    user_id: int = 0
    product_name: str = ""
    sku_code: str = ""
    category_name: str = ""
    material_cost: float = 0.0
    labor_cost: float = 0.0
    packaging_cost: float = 0.0
    shipping_cost: float = 0.0
    other_cost: float = 0.0
    total_cost: float = 0.0
    expected_profit_margin: float = 0.0
    suggested_supply_price: float = 0.0
    product_images: str = ""
    product_description: str = ""
    is_full_commission: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class PricingAdvice:
    product_id: int
    sku_code: str
    product_name: str
    total_cost: float
    min_safe_price: float
    max_safe_price: float
    suggested_price: float
    profit_margin: float
    platform_price_range_low: float
    platform_price_range_high: float
    risk_level: str
    advice_detail: str


@dataclass
class ExportData:
    sku_code: str
    product_name: str
    cost_price: float
    suggested_supply_price: float
    min_safe_price: float
    max_safe_price: float
    expected_margin: float
    risk_level: str

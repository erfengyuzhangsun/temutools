from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, List
from enum import Enum


@dataclass
class ServiceResult:
    success: bool
    message: str = ""
    data: Any = None
    error_code: str = ""


@dataclass
class InventoryItem:
    sku: str
    product_name: str
    current_stock: int
    safety_stock: int
    daily_avg_sales: float = 0.0
    lead_time_days: int = 7
    status: str = "normal"
    category: str = ""
    cost_price: float = 0.0


@dataclass
class ReplenishmentSuggestion:
    sku: str
    product_name: str
    current_stock: int
    suggested_quantity: int
    suggested_order_date: str
    estimated_days_until_stockout: int
    daily_avg_sales: float
    priority: str = "normal"

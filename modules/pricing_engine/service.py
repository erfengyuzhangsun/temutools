import logging
from datetime import datetime, timedelta
from typing import List, Optional
from modules.pricing_engine.schemas import CostBreakdown, PriceSuggestion, AdjustmentRecord
from modules.pricing_engine.config import MODULE_CONFIG
from common.api_client_factory import get_api_client, is_mock_mode

logger = logging.getLogger(__name__)


class PricingEngine:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def calculate_supply_price(
        self, sku_code: str, product_name: str,
        material_cost: float, labor_cost: float,
        packaging_cost: float, shipping_cost: float,
        other_cost: float,
        is_full_commission: bool = True,
        expected_margin: Optional[float] = None,
    ) -> PriceSuggestion:
        total_cost = round(
            material_cost + labor_cost + packaging_cost + shipping_cost + other_cost, 2
        )
        cost_breakdown = CostBreakdown(
            material_cost=material_cost,
            labor_cost=labor_cost,
            packaging_cost=packaging_cost,
            shipping_cost=shipping_cost,
            other_cost=other_cost,
            total_cost=total_cost,
        )

        mode = "full_commission" if is_full_commission else "half_commission"
        commission_rate = (
            MODULE_CONFIG["full_commission_commission_rate"]["default"]
            if is_full_commission
            else MODULE_CONFIG["half_commission_commission_rate"]["default"]
        )
        shipping_subsidy = (
            MODULE_CONFIG["full_commission_shipping_subsidy"]["default"]
            if is_full_commission
            else 0.0
        )
        safe_buffer = MODULE_CONFIG["safe_margin_buffer"]["default"]

        if expected_margin is None:
            expected_margin = 20.0

        suggested_price = round(total_cost * (1 + expected_margin / 100), 2)
        commission_amount = round(suggested_price * commission_rate, 2)
        net_profit = round(suggested_price - total_cost - commission_amount + shipping_subsidy, 2)
        net_profit_margin = round(
            (net_profit / suggested_price) * 100 if suggested_price > 0 else 0, 1
        )

        min_acceptable_margin = expected_margin * 0.6
        min_acceptable_price = round(total_cost * (1 + min_acceptable_margin / 100), 2)
        max_safe_price = round(suggested_price * 1.2, 2)

        platform_sale_price = self._estimate_platform_sale_price(suggested_price)

        warnings = []
        if net_profit_margin < safe_buffer:
            warnings.append(f"净利润率{net_profit_margin}%低于安全缓冲线{safe_buffer}%，存在二次核价风险")
        if net_profit <= 0:
            warnings.append("净利润为负，不可接受！请提高供货价或降低成本")
        if commission_amount > suggested_price * 0.2:
            warnings.append(f"平台佣金({commission_amount})占供货价比例偏高")
        if suggested_price < total_cost * 1.1:
            warnings.append("供货价仅比成本高10%，利润空间非常有限")

        risk_level = "safe" if not warnings else ("warning" if len(warnings) <= 2 else "risky")

        return PriceSuggestion(
            sku_code=sku_code,
            product_name=product_name,
            cost_breakdown=cost_breakdown,
            mode=mode,
            suggested_supply_price=suggested_price,
            platform_sale_price=platform_sale_price,
            commission_amount=commission_amount,
            shipping_subsidy=shipping_subsidy,
            net_profit=net_profit,
            net_profit_margin=net_profit_margin,
            min_acceptable_price=min_acceptable_price,
            max_safe_price=max_safe_price,
            risk_level=risk_level,
            warnings=warnings,
        )

    def _estimate_platform_sale_price(self, supply_price: float) -> Optional[float]:
        return round(supply_price * 1.8, 2)

    def evaluate_adjustment_risk(self, current_price: float, new_price: float) -> dict:
        change_ratio = (new_price - current_price) / current_price if current_price > 0 else 0
        abs_change = abs(change_ratio) * 100
        step_limit = MODULE_CONFIG["price_adjustment_step_ratio"]["default"]

        risk_assessment = {
            "can_adjust": True,
            "risk_level": "low",
            "warnings": [],
            "change_percent": round(abs_change, 1),
        }

        if abs_change > step_limit * 100:
            risk_assessment["warnings"].append(
                f"调价幅度{abs_change:.1f}%超过安全上限{step_limit*100:.0f}%，可能触发平台风控"
            )
            risk_assessment["risk_level"] = "high"

        if change_ratio > 0:
            risk_assessment["warnings"].append("涨价操作建议谨慎，需确认有合理的涨价依据")
            if risk_assessment["risk_level"] == "low":
                risk_assessment["risk_level"] = "medium"

        cooldown_hours = MODULE_CONFIG["price_adjustment_cooldown_hours"]["default"]
        today_count = self._get_today_adjustment_count("")
        max_per_day = MODULE_CONFIG["max_price_adjustments_per_day"]["default"]
        if today_count >= max_per_day:
            risk_assessment["warnings"].append(f"今日调价次数已达上限({max_per_day}次)")
            risk_assessment["can_adjust"] = False
            risk_assessment["risk_level"] = "blocked"

        return risk_assessment

    def _get_today_adjustment_count(self, sku_code: str) -> int:
        from db import execute_query
        today = datetime.now().strftime("%Y-%m-%d")
        rows = execute_query(
            "SELECT COUNT(*) as cnt FROM temu_price_adjustments "
            "WHERE user_id=? AND date(created_at)=?",
            (self.user_id, today), fetch=True,
        )
        return rows[0]["cnt"] if rows else 0

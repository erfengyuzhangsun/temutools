import logging
from datetime import datetime, timedelta
from typing import List, Optional
from modules.risk_guard.schemas import RiskRule, PricingCheckResult, RiskHistory

logger = logging.getLogger(__name__)


class RiskGuardService:
    RULES = [
        RiskRule(
            rule_id="R001",
            name="毛利率低于安全线",
            description="供货价毛利率低于最低安全毛利率时，禁止调低价格，防止二次核价",
            severity="high",
            condition_desc="毛利率 < 最低安全线",
        ),
        RiskRule(
            rule_id="R002",
            name="单次调价幅度超限",
            description="单次调价幅度超过设定的安全百分比上限，需分多次逐步调整",
            severity="high",
            condition_desc="调价幅度 > 单次最大调价幅度",
        ),
        RiskRule(
            rule_id="R003",
            name="频繁调价触发风控",
            description="同一SKU在短时间内多次调价，可能被平台风控系统标记为异常",
            severity="medium",
            condition_desc="24小时内调价次数 > 最大允许次数",
        ),
        RiskRule(
            rule_id="R004",
            name="降价后价格低于成本",
            description="降价后的供货价低于成本价，属于亏损销售，可能触发平台关注",
            severity="critical",
            condition_desc="新价格 < 成本价",
        ),
        RiskRule(
            rule_id="R005",
            name="涨价幅度异常",
            description="突然大幅涨价可能被平台判定为价格操纵，需提供合理依据",
            severity="medium",
            condition_desc="涨价幅度 > 安全上涨幅度",
        ),
        RiskRule(
            rule_id="R006",
            name="活动期间价格锁定",
            description="活动商品在活动期间禁止调价，否则可能被取消活动资格",
            severity="high",
            condition_desc="商品处于活动期间且价格非活动价",
        ),
    ]

    def __init__(self, user_id: int):
        self.user_id = user_id
        self._ensure_tables()

    @staticmethod
    def _ensure_tables():
        try:
            from db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temu_risk_guard_logs (
                    log_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    sku_code VARCHAR(100) DEFAULT '',
                    operation VARCHAR(50) NOT NULL,
                    detail TEXT,
                    risk_level VARCHAR(20) DEFAULT 'low',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.close()
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"确保风控日志表存在时出错: {e}")

    def get_all_rules(self) -> List[RiskRule]:
        return self.RULES

    def check_pricing_safety(
        self, sku_code: str, product_name: str,
        current_price: float, new_price: float,
        cost_price: float,
        is_activity_period: bool = False,
        is_in_activity: bool = False,
    ) -> PricingCheckResult:
        triggered = []
        risk_levels = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        change_percent = ((new_price - current_price) / current_price) * 100 if current_price > 0 else 0

        if cost_price > 0:
            current_margin = ((current_price - cost_price) / cost_price) * 100
            new_margin = ((new_price - cost_price) / cost_price) * 100
        else:
            current_margin = 0
            new_margin = 0

        min_safe_margin = 10.0

        if new_margin < min_safe_margin:
            triggered.append({
                "rule_id": "R001", "detail": f"新毛利率{new_margin:.1f}%低于安全线{min_safe_margin}%"
            })
            risk_levels["high"] += 1

        max_single_change = 5.0
        if abs(change_percent) > max_single_change:
            triggered.append({
                "rule_id": "R002", "detail": f"调价幅度{abs(change_percent):.1f}%超过单次上限{max_single_change}%"
            })
            risk_levels["high"] += 1

        recent_count = self._get_recent_adjustment_count(sku_code)
        max_frequent = 3
        if recent_count >= max_frequent:
            triggered.append({
                "rule_id": "R003", "detail": f"24小时内调价{recent_count}次，超过上限{max_frequent}次"
            })
            risk_levels["medium"] += 1

        if cost_price > 0 and new_price < cost_price:
            triggered.append({
                "rule_id": "R004", "detail": f"新价格¥{new_price:.2f}低于成本价¥{cost_price:.2f}"
            })
            risk_levels["critical"] += 1

        max_increase = 10.0
        if change_percent > max_increase:
            triggered.append({
                "rule_id": "R005", "detail": f"涨价幅度{change_percent:.1f}%超过安全上限{max_increase}%"
            })
            risk_levels["medium"] += 1

        if is_activity_period and is_in_activity:
            triggered.append({
                "rule_id": "R006", "detail": "该商品处于活动期间，建议不要调价"
            })
            risk_levels["high"] += 1

        if risk_levels["critical"] > 0:
            overall_risk = "critical"
            passed = False
        elif risk_levels["high"] > 0:
            overall_risk = "high"
            passed = False
        elif risk_levels["medium"] > 0:
            overall_risk = "medium"
            passed = True
        else:
            overall_risk = "low"
            passed = True

        triggered_descriptions = [t["detail"] for t in triggered]

        if passed:
            advice = "✅ 调价方案通过风控校验，可以执行"
            if triggered:
                advice += "（注意：" + "；".join(triggered_descriptions) + "）"
        else:
            advice = "❌ 调价被风控拦截：\n" + "\n".join(f"- {t}" for t in triggered_descriptions)
            advice += "\n建议：调整调价幅度或降低调价频率后再试"

        result = PricingCheckResult(
            sku_code=sku_code,
            product_name=product_name,
            current_supply_price=current_price,
            new_supply_price=new_price,
            change_percent=round(change_percent, 2),
            passed=passed,
            triggered_rules=triggered_descriptions,
            risk_level=overall_risk,
            advice=advice,
            checked_at=datetime.now().isoformat(),
        )

        self._save_check_history(sku_code, result)
        return result

    def _get_recent_adjustment_count(self, sku_code: str) -> int:
        from db import execute_query
        since = (datetime.now() - timedelta(hours=24)).isoformat()
        rows = execute_query(
            "SELECT COUNT(*) as cnt FROM temu_risk_guard_logs "
            "WHERE user_id=? AND sku_code=? AND created_at>=? AND operation='price_check'",
            (self.user_id, sku_code, since), fetch=True,
        )
        return rows[0]["cnt"] if rows else 0

    def _save_check_history(self, sku_code: str, result: PricingCheckResult):
        from db import execute_query
        try:
            execute_query("""
                INSERT INTO temu_risk_guard_logs
                (user_id, sku_code, operation, detail, risk_level)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.user_id, sku_code, "price_check",
                f"调价 {result.current_supply_price}→{result.new_supply_price} ({result.change_percent}%)",
                result.risk_level,
            ))
        except Exception as e:
            logger.warning(f"保存风控日志失败: {e}")

    def get_recent_checks(self, limit: int = 50) -> List[RiskHistory]:
        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_risk_guard_logs "
            "WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (self.user_id, limit), fetch=True,
        ) or []
        return [
            RiskHistory(
                history_id=r.get("log_id", 0),
                sku_code=r.get("sku_code", ""),
                operation=r.get("operation", ""),
                detail=r.get("detail", ""),
                risk_level=r.get("risk_level", ""),
                created_at=str(r.get("created_at", "")),
            )
            for r in rows
        ]

PLAN_HIERARCHY = {"basic": 0, "pro": 1, "enterprise": 2, "lifetime": 3}

REQUIRED_PLAN = {
    "api_sync": "pro",
    "api_guide": "pro",
    "pricing": "pro",
    "pricing_adj": "pro",
    "analysis": "pro",
    "scheduler": "pro",
    "message": "pro",
    "activity": "pro",
    "review_monitor": "pro",
    "shipping": "pro",
    "inventory": "pro",
    "risk_guard": "pro",
    "factory_cost": "enterprise",
    "supplier": "enterprise",
    "batch_ops": "enterprise",
    "product_research": "enterprise",
}


def _get_plan_type_from_db(user_id: int) -> str:
    try:
        from db import execute_query
        rows = execute_query(
            "SELECT plan_type FROM temu_users WHERE user_id = ?",
            (user_id,), fetch=True,
        )
        if rows:
            return rows[0].get("plan_type", "basic")
    except Exception:
        pass
    return "basic"


def _get_plan_type_from_session() -> str:
    try:
        from auth import get_user_plan_type
        return get_user_plan_type() or "basic"
    except Exception:
        pass
    return "basic"


def get_user_plan_type(user_id: int = None) -> str:
    plan_type = _get_plan_type_from_session()
    if plan_type == "basic" and user_id:
        plan_type = _get_plan_type_from_db(user_id)
    return plan_type


def check_plan_access(module_name: str, user_id: int = None) -> bool:
    required = REQUIRED_PLAN.get(module_name)
    if required is None:
        return True
    plan_type = get_user_plan_type(user_id)
    return PLAN_HIERARCHY.get(plan_type, 0) >= PLAN_HIERARCHY.get(required, 1)

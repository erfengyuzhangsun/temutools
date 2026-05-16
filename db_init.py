"""
数据库统一初始化入口
在应用启动时调用，确保所有模块的数据表都已创建
"""
import logging

logger = logging.getLogger(__name__)

# 记录已初始化的模块，防止重复执行
_initialized_modules = set()


def initialize_all_tables():
    """初始化全部模块的数据表"""
    if _initialized_modules:
        logger.info("数据库表已初始化，跳过")
        return

    logger.info("开始初始化全部模块数据表...")

    # 1. 基础表（原有系统）
    from db import initialize_database
    initialize_database()
    _initialized_modules.add("base")
    logger.info("[1/8] 基础表初始化完成")

    # 2. P0-模块1: API同步
    try:
        from modules.api_sync.models import initialize_sync_tables
        initialize_sync_tables()
        _initialized_modules.add("api_sync")
        logger.info("[2/8] API同步表初始化完成")
    except Exception as e:
        logger.warning(f"API同步表初始化失败: {e}")

    # 3. P0-模块2: 核价
    try:
        from modules.pricing.models import initialize_pricing_tables
        initialize_pricing_tables()
        _initialized_modules.add("pricing")
        logger.info("[3/8] 核价表初始化完成")
    except Exception as e:
        logger.warning(f"核价表初始化失败: {e}")

    # 4. P0-模块3: 调度中心
    try:
        from modules.scheduler.models import initialize_scheduler_tables
        initialize_scheduler_tables()
        _initialized_modules.add("scheduler")
        logger.info("[4/8] 调度中心表初始化完成")
    except Exception as e:
        logger.warning(f"调度中心表初始化失败: {e}")

    # 5. P1-模块4: 库存管理
    try:
        from modules.inventory.models import initialize_tables
        initialize_tables()
        _initialized_modules.add("inventory")
        logger.info("[5/8] 库存管理表初始化完成")
    except Exception as e:
        logger.warning(f"库存管理表初始化失败: {e}")

    # 6. P1-模块5: 数据分析
    try:
        from modules.analysis.models import initialize_tables
        initialize_tables()
        _initialized_modules.add("analysis")
        logger.info("[6/8] 数据分析表初始化完成")
    except Exception as e:
        logger.warning(f"数据分析表初始化失败: {e}")

    # 7. P1-模块6/7/8: 调价/财务/大屏
    for mod_name, mod_import in [
        ("pricing_adj", "modules.pricing_adj.models"),
        ("finance", "modules.finance.models"),
        ("dashboard", "modules.dashboard.models"),
    ]:
        try:
            mod = __import__(mod_import, fromlist=["initialize_tables"])
            mod.initialize_tables()
            _initialized_modules.add(mod_name)
        except Exception as e:
            logger.warning(f"{mod_name}表初始化失败: {e}")
    logger.info("[7/8] 调价/财务/大屏表初始化完成")

    # 8. P2+P3: 消息/发货/活动/风控/选品/供应商等
    for mod_name, mod_import in [
        ("message", "modules.message.models"),
        ("factory_cost", "modules.factory_cost.models"),
        ("risk_guard", "modules.risk_guard.models"),
    ]:
        try:
            mod = __import__(mod_import, fromlist=["initialize_tables"])
            mod.initialize_tables()
            _initialized_modules.add(mod_name)
        except Exception as e:
            logger.warning(f"{mod_name}表初始化失败: {e}")

    try:
        from common.models_p2p3 import initialize_tables
        initialize_tables()
        _initialized_modules.add("p2p3_common")
        logger.info("[8/8] P2/P3模块表初始化完成")
    except Exception as e:
        logger.warning(f"P2/P3模块表初始化失败: {e}")

    logger.info(f"全部模块数据表初始化完毕 | 已初始化: {len(_initialized_modules)} 组")
    return True


def get_initialized_modules():
    """返回已初始化的模块列表"""
    return sorted(_initialized_modules)

import streamlit as st
import pandas as pd
from datetime import datetime
from modules.risk_guard.service import RiskGuardService
from modules.risk_guard.config import MODULE_CONFIG


def show_page():
    st.markdown('<p class="main-header">🛡️ 风控防二次核价</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">调价合规校验 · 平台规则守护 · 资金安全防护</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)
    service = RiskGuardService(user_id)

    tab1, tab2, tab3 = st.tabs(["🔍 调价安全检测", "📋 风控规则", "📊 检测历史"])

    with tab1:
        _render_safety_check(service)

    with tab2:
        _render_rules()

    with tab3:
        _render_history(service)

    st.markdown("---")
    st.caption("风控防二次核价模块 | 纯规则引擎，零API依赖，所有调价操作先审后调")


def _render_safety_check(service: RiskGuardService):
    st.markdown("#### 调价安全检测")
    st.caption("在提交调价给平台之前，先用风控引擎检测是否存在触发二次核价或账号风控的风险")

    col1, col2 = st.columns(2)
    with col1:
        sku_code = st.text_input("SKU编码", placeholder="如：SKU_BL001", key="sc_sku")
        product_name = st.text_input("产品名称", placeholder="如：北欧风收纳盒", key="sc_name")
        current_price = st.number_input("当前供货价 (元)", min_value=0.0, step=0.5, format="%.2f", key="sc_cur")
    with col2:
        new_price = st.number_input("拟调整供货价 (元)", min_value=0.0, step=0.5, format="%.2f", key="sc_new")
        cost_price = st.number_input("生产总成本 (元)", min_value=0.0, step=0.5, format="%.2f", key="sc_cost", help="从工厂成本模块获取")
        is_activity = st.checkbox("该商品正在参与平台活动", value=False, key="sc_act")

    if st.button("🔍 检测调价风险", type="primary", use_container_width=True):
        if not sku_code or current_price <= 0 or new_price <= 0:
            st.error("请填写完整的检测信息")
        else:
            result = service.check_pricing_safety(
                sku_code=sku_code, product_name=product_name,
                current_price=current_price, new_price=new_price,
                cost_price=cost_price, is_activity_period=is_activity,
                is_in_activity=is_activity,
            )

            risk_labels = {
                "low": ("🟢 低风险", "success"),
                "medium": ("🟡 中等风险", "warning"),
                "high": ("🔴 高风险", "error"),
                "critical": ("⛔ 严重风险", "error"),
            }
            label, color = risk_labels.get(result.risk_level, ("⚪ 未知", "info"))

            st.markdown(f"##### 检测结果：{label}")
            st.markdown(f"**调价：** ¥{result.current_supply_price:.2f} → ¥{result.new_supply_price:.2f} "
                       f"({result.change_percent:+.2f}%)")

            if result.passed:
                st.success(result.advice)
            else:
                st.error(result.advice)

            if result.triggered_rules:
                st.warning("**触发的风控规则：**")
                for rule in result.triggered_rules:
                    st.markdown(f"- {rule}")


def _render_rules():
    st.markdown("#### 风控规则集")
    st.caption("以下规则对所有调价操作进行前置检查，确保合规运营")

    rules = [
        {"规则ID": "R001", "规则名称": "毛利率低于安全线", "严重程度": "🔴 高", "说明": "供货价毛利率低于最低安全毛利率时禁止调低价格"},
        {"规则ID": "R002", "规则名称": "单次调价幅度超限", "严重程度": "🔴 高", "说明": "单次调价幅度超过5%需分多次调整"},
        {"规则ID": "R003", "规则名称": "频繁调价触发风控", "严重程度": "🟡 中", "说明": "24小时内同一SKU调价超过3次将被限制"},
        {"规则ID": "R004", "规则名称": "降价后价格低于成本", "严重程度": "⛔ 致命", "说明": "供货价低于成本价直接拦截，强制禁止"},
        {"规则ID": "R005", "规则名称": "涨价幅度异常", "严重程度": "🟡 中", "说明": "单次涨价超过10%需提供合理依据"},
        {"规则ID": "R006", "规则名称": "活动期间价格锁定", "严重程度": "🔴 高", "说明": "活动商品在活动期间禁止调价"},
    ]
    st.dataframe(pd.DataFrame(rules), width='stretch', hide_index=True)

    st.markdown("#### 被拦截后怎么办？")
    st.info("""
    **正确做法：**
    1. 如果毛利率低于安全线 → 先优化成本（降低材料/人工/包装成本）
    2. 如果想大幅调价 → 分多次小幅度调整，每次间隔24小时以上
    3. 如果涨价 → 准备涨价依据（如原材料涨价、工艺升级等）
    4. 如果是活动商品 → 等活动结束后再调价

    **错误做法（触发风控）：**
    1. 频繁调价 → 平台标记为价格操纵
    2. 亏本销售 → 平台触发二次核价，强制调高供货价
    3. 活动期间调价 → 取消活动资格
    """)


def _render_history(service: RiskGuardService):
    st.markdown("#### 检测历史")
    logs = service.get_recent_checks()
    if not logs:
        st.info("暂无检测记录")
        return

    records = []
    for log in logs:
        risk_icons = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "⛔"}
        records.append({
            "时间": log.created_at,
            "SKU": log.sku_code,
            "操作": log.operation,
            "详情": log.detail,
            "风险等级": f"{risk_icons.get(log.risk_level, '⚪')} {log.risk_level}",
        })
    st.dataframe(pd.DataFrame(records), width='stretch', hide_index=True)

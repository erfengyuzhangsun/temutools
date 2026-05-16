import streamlit as st
import pandas as pd
from datetime import datetime
from modules.pricing_engine.service import PricingEngine
from modules.factory_cost.service import FactoryCostService
from common.api_client_factory import is_mock_mode


def show_page():
    st.markdown('<p class="main-header">🧮 全托管核价引擎</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">成本→供货价测算 · 利润分析 · 安全调价区间 · 风控预警</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)
    engine = PricingEngine(user_id)

    if is_mock_mode():
        st.info("🔔 当前为模拟模式，未配置店铺API凭证。请先在「API对接与数据同步」→「店铺管理」中绑定店铺并填写API凭证")

    tab1, tab2, tab3 = st.tabs(["💰 成本测算", "📊 批量分析", "📈 调价风控"])

    with tab1:
        _render_cost_calculator(engine)

    with tab2:
        _render_batch_analysis(user_id, engine)

    with tab3:
        _render_adjustment_risk(user_id, engine)

    st.markdown("---")
    st.caption("全托管核价引擎 | 专为自有工厂卖家设计，纯算法计算，零API依赖")


def _render_cost_calculator(engine: PricingEngine):
    st.markdown("#### 单产品核价测算")
    st.caption("输入工厂成本，自动计算安全供货价和利润分析")

    col1, col2 = st.columns(2)
    with col1:
        sku_code = st.text_input("SKU编码", placeholder="如：SKU_BL001", key="ce_sku")
        product_name = st.text_input("产品名称", placeholder="如：北欧风收纳盒", key="ce_name")
        material_cost = st.number_input("原材料成本 (元)", min_value=0.0, step=0.5, format="%.2f", key="ce_mat")
        labor_cost = st.number_input("人工成本 (元)", min_value=0.0, step=0.5, format="%.2f", key="ce_lab")
    with col2:
        packaging_cost = st.number_input("包装成本 (元)", min_value=0.0, step=0.5, format="%.2f", key="ce_pkg")
        shipping_cost = st.number_input("物流成本 (元)", min_value=0.0, step=0.5, format="%.2f", key="ce_shp")
        other_cost = st.number_input("其他成本 (元)", min_value=0.0, step=0.5, format="%.2f", key="ce_oth")
        is_full_commission = st.checkbox("全托管模式", value=True, help="全托管 vs 半托管")
        expected_margin = st.slider("期望毛利率 (%)", 1.0, 80.0, 20.0, 0.5, key="ce_margin")

    if st.button("🧮 测算供货价", type="primary", use_container_width=True):
        if not sku_code or not product_name:
            st.error("请输入SKU编码和产品名称")
        else:
            result = engine.calculate_supply_price(
                sku_code=sku_code, product_name=product_name,
                material_cost=material_cost, labor_cost=labor_cost,
                packaging_cost=packaging_cost, shipping_cost=shipping_cost,
                other_cost=other_cost,
                is_full_commission=is_full_commission,
                expected_margin=expected_margin,
            )
            _display_price_suggestion(result)


def _display_price_suggestion(result):
    risk_colors = {"safe": "🟢", "warning": "🟡", "risky": "🔴"}
    st.markdown("---")
    st.markdown(f"#### 📋 核价结果 {risk_colors.get(result.risk_level, '⚪')}")

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("建议供货价", f"¥{result.suggested_supply_price:.2f}")
        st.metric("可接受最低价", f"¥{result.min_acceptable_price:.2f}")
    with col_m2:
        st.metric("预计平台售价", f"¥{result.platform_sale_price:.2f}" if result.platform_sale_price else "待定")
        st.metric("安全价格上限", f"¥{result.max_safe_price:.2f}")
    with col_m3:
        st.metric("净利润", f"¥{result.net_profit:.2f}")
        st.metric("净利润率", f"{result.net_profit_margin:.1f}%")

    st.markdown("##### 💰 成本明细")
    cost_df = pd.DataFrame([
        {"项目": "原材料", "金额": f"¥{result.cost_breakdown.material_cost:.2f}"},
        {"项目": "人工", "金额": f"¥{result.cost_breakdown.labor_cost:.2f}"},
        {"项目": "包装", "金额": f"¥{result.cost_breakdown.packaging_cost:.2f}"},
        {"项目": "物流", "金额": f"¥{result.cost_breakdown.shipping_cost:.2f}"},
        {"项目": "其他", "金额": f"¥{result.cost_breakdown.other_cost:.2f}"},
        {"项目": "---", "金额": "---"},
        {"项目": "总成本", "金额": f"¥{result.cost_breakdown.total_cost:.2f}"},
        {"项目": "平台佣金", "金额": f"-¥{result.commission_amount:.2f}"},
        {"项目": "运费补贴", "金额": f"+¥{result.shipping_subsidy:.2f}"},
    ])
    st.dataframe(cost_df, width='stretch', hide_index=True)

    if result.warnings:
        st.markdown("##### ⚠️ 风险提示")
        for w in result.warnings:
            st.warning(w)
    else:
        st.success("✅ 当前定价方案安全，无风险预警")


def _render_batch_analysis(user_id: int, engine: PricingEngine):
    st.markdown("#### 批量核价分析")
    st.caption("基于已录入的工厂成本数据，批量计算核价建议")

    fc_service = FactoryCostService(user_id)
    products = fc_service.get_products()

    if not products:
        st.info("暂无产品成本数据，请先在「工厂成本管理」模块录入产品")
        return

    results = []
    for p in products:
        result = engine.calculate_supply_price(
            sku_code=p.sku_code, product_name=p.product_name,
            material_cost=p.material_cost, labor_cost=p.labor_cost,
            packaging_cost=p.packaging_cost, shipping_cost=p.shipping_cost,
            other_cost=p.other_cost,
            is_full_commission=p.is_full_commission,
            expected_margin=p.expected_profit_margin,
        )
        risk_icon = {"safe": "🟢", "warning": "🟡", "risky": "🔴"}.get(result.risk_level, "⚪")
        results.append({
            "产品": p.product_name,
            "SKU": p.sku_code,
            "总成本": f"¥{result.cost_breakdown.total_cost:.2f}",
            "建议供货价": f"¥{result.suggested_supply_price:.2f}",
            "最低可接价": f"¥{result.min_acceptable_price:.2f}",
            "净利润率": f"{result.net_profit_margin:.1f}%",
            "风险评估": f"{risk_icon} {result.risk_level}",
        })

    df = pd.DataFrame(results)
    st.dataframe(df, width='stretch', hide_index=True)

    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "📥 导出批量核价表 (CSV)", data=csv,
        file_name=f"批量核价分析_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv", use_container_width=True,
    )


def _render_adjustment_risk(user_id: int, engine: PricingEngine):
    st.markdown("#### 调价风控评估")
    st.caption("在调整供货价前，评估调价幅度是否在安全范围内")

    col1, col2 = st.columns(2)
    with col1:
        cur_price = st.number_input("当前供货价 (元)", min_value=0.0, step=0.5, format="%.2f", key="ar_cur")
    with col2:
        new_price = st.number_input("拟调整供货价 (元)", min_value=0.0, step=0.5, format="%.2f", key="ar_new")

    if st.button("🔍 评估调价风险", type="primary", use_container_width=True):
        if cur_price <= 0 or new_price <= 0:
            st.error("请输入有效的当前价和拟调整价")
        else:
            assessment = engine.evaluate_adjustment_risk(cur_price, new_price)
            change = ((new_price - cur_price) / cur_price) * 100

            st.metric("调价幅度", f"{change:+.1f}%")

            risk_labels = {"low": "🟢 低风险", "medium": "🟡 中等风险", "high": "🔴 高风险", "blocked": "⛔ 禁止调价"}
            st.info(f"**风险评估：** {risk_labels.get(assessment['risk_level'], '未知')}")

            if assessment["can_adjust"]:
                st.success("✅ 可以进行调价操作")
            else:
                st.error("❌ 当前不可调价")

            if assessment["warnings"]:
                st.warning("**风险提示：**")
                for w in assessment["warnings"]:
                    st.markdown(f"- {w}")

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from modules.factory_cost.service import FactoryCostService
from modules.factory_cost.schemas import ProductInfo
from modules.factory_cost.config import MODULE_CONFIG


def show_page():
    st.markdown('<p class="main-header">🏭 工厂成本管理</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">自有产品资料录入 · 生产成本核算 · 安全供货价建议</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)
    service = FactoryCostService(user_id)

    tab1, tab2, tab3 = st.tabs(["📝 产品录入", "📋 产品列表", "📊 核价分析"])

    with tab1:
        _render_product_form(service)

    with tab2:
        _render_product_list(service)

    with tab3:
        _render_pricing_analysis(service)

    st.markdown("---")
    st.caption("工厂成本管理 | 专为全托管自有工厂卖家设计，数据仅存本地，安全合规")


def _render_product_form(service: FactoryCostService):
    st.markdown("#### 录入产品资料")

    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("产品名称 *", placeholder="如：北欧风简约收纳盒套装")
        sku_code = st.text_input("SKU编码 *", placeholder="如：SKU_BL001")
    with col2:
        category_name = st.selectbox(
            "产品类目",
            ["家居百货", "3C数码", "服装鞋包", "美妆个护", "玩具母婴", "食品饮料", "运动户外", "其他"],
            index=0,
        )
        is_full_commission = st.checkbox("全托管模式", value=True, help="全托管卖家适用独立定价规则")

    st.markdown("##### 💰 成本构成（单位：元）")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        material_cost = st.number_input("原材料成本", min_value=0.0, step=0.5, format="%.2f", key="mat_cost")
        labor_cost = st.number_input("人工成本", min_value=0.0, step=0.5, format="%.2f", key="lab_cost")
    with col_c2:
        packaging_cost = st.number_input("包装成本", min_value=0.0, step=0.5, format="%.2f", key="pkg_cost")
        shipping_cost = st.number_input("物流/运费成本", min_value=0.0, step=0.5, format="%.2f", key="shp_cost")
    with col_c3:
        other_cost = st.number_input("其他成本", min_value=0.0, step=0.5, format="%.2f", key="oth_cost")

    total_cost = round(material_cost + labor_cost + packaging_cost + shipping_cost + other_cost, 2)
    st.metric("总成本", f"¥{total_cost:.2f}")

    expected_margin = st.slider(
        "期望毛利率 (%)",
        min_value=1.0, max_value=100.0,
        value=MODULE_CONFIG["default_expected_margin"]["default"],
        step=0.5,
    )
    suggested_price = round(total_cost * (1 + expected_margin / 100), 2)
    st.metric("建议供货价", f"¥{suggested_price:.2f}")
    st.caption(f"按总成本 ¥{total_cost:.2f} + 期望毛利率 {expected_margin:.1f}% 计算")

    product_description = st.text_area("产品描述", placeholder="产品特点、材质、工艺等补充说明", height=100)

    if st.button("💾 保存产品", type="primary", use_container_width=True):
        if not product_name or not sku_code:
            st.error("产品名称和SKU编码为必填项")
        else:
            existing = service.get_product_by_sku(sku_code)
            product = ProductInfo(
                user_id=st.session_state.get("user_id", 1),
                product_name=product_name,
                sku_code=sku_code,
                category_name=category_name,
                material_cost=material_cost,
                labor_cost=labor_cost,
                packaging_cost=packaging_cost,
                shipping_cost=shipping_cost,
                other_cost=other_cost,
                expected_profit_margin=expected_margin,
                product_description=product_description,
                is_full_commission=is_full_commission,
            )
            product_id = service.save_product(product)
            if product_id > 0:
                action = "更新" if existing else "新增"
                st.success(f"✅ {action}产品成功！(ID: {product_id})")
                st.rerun()
            else:
                st.error("❌ 保存失败，请检查数据")


def _render_product_list(service: FactoryCostService):
    st.markdown("#### 已录入产品")
    products = service.get_products()
    if not products:
        st.info("暂无产品数据，请在「产品录入」页签添加")
        return

    for p in products:
        with st.expander(f"📦 {p.product_name} ({p.sku_code})", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**类目：** {p.category_name}")
                st.markdown(f"**模式：** {'全托管' if p.is_full_commission else '半托管'}")
                st.markdown(f"**材料：** ¥{p.material_cost:.2f} | **人工：** ¥{p.labor_cost:.2f}")
            with col2:
                st.markdown(f"**包装：** ¥{p.packaging_cost:.2f} | **物流：** ¥{p.shipping_cost:.2f}")
                st.markdown(f"**其他：** ¥{p.other_cost:.2f}")
                st.markdown(f"**总成本：** ¥{p.total_cost:.2f}")
            with col3:
                st.markdown(f"**期望毛利率：** {p.expected_profit_margin:.1f}%")
                st.markdown(f"**建议供货价：** ¥{p.suggested_supply_price:.2f}")
                st.markdown(f"**创建时间：** {p.created_at}")

            if p.product_description:
                st.markdown(f"**描述：** {p.product_description}")

            if st.button("🗑️ 删除", key=f"del_{p.product_id}"):
                service.delete_product(p.product_id)
                st.rerun()


def _render_pricing_analysis(service: FactoryCostService):
    st.markdown("#### 核价分析 & 安全供货价建议")
    st.caption("基于工厂成本 + 期望毛利 + 风控规则自动计算安全报价区间")

    products = service.get_products()
    if not products:
        st.info("暂无产品，请先在「产品录入」页签添加产品")
        return

    advices = service.batch_calculate_pricing()

    data = []
    for adv in advices:
        risk_icon = "🟢" if adv.risk_level == "safe" else "🔴"
        data.append({
            "产品": adv.product_name,
            "SKU": adv.sku_code,
            "总成本": f"¥{adv.total_cost:.2f}",
            "建议供货价": f"¥{adv.suggested_price:.2f}",
            "安全下限": f"¥{adv.min_safe_price:.2f}",
            "安全上限": f"¥{adv.max_safe_price:.2f}",
            "预计毛利率": f"{adv.profit_margin:.1f}%",
            "风险": f"{risk_icon} {'安全' if adv.risk_level == 'safe' else '关注'}",
        })
    df = pd.DataFrame(data)
    st.dataframe(df, width='stretch', hide_index=True)

    st.markdown("#### 详细分析")
    for adv in advices:
        risk_icon = "🟢" if adv.risk_level == "safe" else "🔴"
        title = f"{risk_icon} {adv.product_name} ({adv.sku_code})"
        with st.expander(title, expanded=adv.risk_level != "safe"):
            st.markdown(f"**建议供货价：** ¥{adv.suggested_price:.2f}")
            st.markdown(f"**安全报价区间：** ¥{adv.min_safe_price:.2f} ~ ¥{adv.max_safe_price:.2f}")
            st.markdown(f"**预计毛利率：** {adv.profit_margin:.1f}%")
            st.markdown(f"**平台核价区间参考：** ¥{adv.platform_price_range_low:.2f} ~ ¥{adv.platform_price_range_high:.2f}")
            st.markdown(f"**分析建议：** {adv.advice_detail}")

    if st.button("📥 导出核价建议表 (CSV)", use_container_width=True):
        export_data = service.export_pricing_data()
        rows = []
        for e in export_data:
            rows.append({
                "SKU": e.sku_code,
                "产品名称": e.product_name,
                "成本价": e.cost_price,
                "建议供货价": e.suggested_supply_price,
                "安全下限": e.min_safe_price,
                "安全上限": e.max_safe_price,
                "期望毛利率": f"{e.expected_margin:.1f}%",
                "风险评估": e.risk_level,
            })
        export_df = pd.DataFrame(rows)
        csv = export_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="⬇️ 下载 CSV",
            data=csv,
            file_name=f"核价建议表_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

import streamlit as st
import asyncio
import pandas as pd
from common.services_p2p3 import ProductResearchService


def show_page():
    st.markdown('<p class="main-header">🔬 选品辅助</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">1688选品采集 · 利润预估 · 侵权检测</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2, tab3 = st.tabs(["🔍 选品采集", "💰 利润预估", "⚠️ 侵权检测"])

    with tab1:
        st.markdown("#### 1688 选品采集")

        col_k1, col_k2 = st.columns([3, 1])
        with col_k1:
            keywords = st.text_input("搜索关键词", placeholder="例如：收纳盒、蓝牙耳机")
        with col_k2:
            limit = st.number_input("采集数量", min_value=1, max_value=20, value=10)

        if st.button("🔍 采集", type="primary", use_container_width=True):
            if not keywords.strip():
                st.error("请输入搜索关键词")
            else:
                service = ProductResearchService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(
                    service.collect_1688(keywords=keywords, limit=limit)
                )
                loop.close()

                if result.success:
                    data = result.data or {}
                    items = data.get("items", [])

                    if items:
                        st.success(f"✅ 采集到 {len(items)} 个商品")

                        df = pd.DataFrame(items)
                        st.dataframe(df, width='stretch')

                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            "📥 导出选品数据 (CSV)",
                            data=csv,
                            file_name="product_research.csv",
                            mime="text/csv",
                        )
                    else:
                        st.info("未采集到商品")
                else:
                    st.error(f"❌ {result.message}")

    with tab2:
        st.markdown("#### 利润预估")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            cost_price = st.number_input("成本价 (¥)", min_value=0.0, value=30.0, step=5.0)
        with col_p2:
            suggested_price = st.number_input(
                "建议售价 (¥)", min_value=0.0, value=75.0, step=5.0,
                help="留空则按成本价的2.5倍自动计算",
            )

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "参考店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("💰 预估利润", type="primary", use_container_width=True):
                product_data = {
                    "price": cost_price,
                    "suggested_price": suggested_price if suggested_price > 0 else cost_price * 2.5,
                }

                service = ProductResearchService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(
                    service.estimate_profit(product_data=product_data, shop_id=shop_id)
                )
                loop.close()

                if result.success:
                    data = result.data or {}
                    st.success("✅ 利润预估完成")

                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("预估利润", f"¥{data.get('estimated_profit', 0):.2f}")
                    col_m2.metric("预估利润率", f"{data.get('estimated_margin', 0):.1f}%")
                    col_m3.metric("建议售价", f"¥{data.get('suggested_price', 0):.2f}")

                    st.markdown("##### 费用明细")
                    detail_cols = st.columns(4)
                    detail_cols[0].metric("成本价", f"¥{data.get('cost', 0):.2f}")
                    detail_cols[1].metric("运费", f"¥{data.get('shipping', 0):.2f}")
                    detail_cols[2].metric("平台费用", f"¥{data.get('platform_fee', 0):.2f}")
                    detail_cols[3].metric("售价", f"¥{data.get('suggested_price', 0):.2f}")
        else:
            st.info("暂无店铺数据")

    with tab3:
        st.markdown("#### 侵权风险检测")

        title = st.text_input("商品标题", placeholder="输入商品标题进行检测")

        if st.button("🔍 检测", type="primary", use_container_width=True):
            if not title.strip():
                st.error("请输入商品标题")
            else:
                service = ProductResearchService(user_id)
                result = service.check_infringement(title)

                if result.success:
                    data = result.data or {}
                    risk = data.get("risk", "low")

                    if risk == "high":
                        st.error("⚠️ 检测到高风险侵权内容")
                        brands = data.get("infringing_brands", [])
                        for b in brands:
                            st.warning(f"🔴 检测到品牌词: {b}")
                        st.error(f"💡 建议: {data.get('suggestion', '')}")
                    else:
                        st.success("✅ 未检测到侵权风险")
                else:
                    st.error(f"❌ {result.message}")

    st.markdown("---")
    st.caption("选品辅助模块 | 数据驱动的选品决策，降低侵权风险")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

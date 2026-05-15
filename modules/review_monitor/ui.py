import streamlit as st
import pandas as pd
from common.services_p2p3 import ReviewMonitorService
from common.async_runner import run as run_async


def show_page():
    st.markdown('<p class="main-header">⭐ 差评监控</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">差评自动同步 · 高风险SKU识别 · 关键词分析</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2 = st.tabs(["🔄 差评同步", "📊 差评分析"])

    with tab1:
        st.markdown("#### 同步并分析差评")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🔄 同步最新评价", type="primary", use_container_width=True):
                    service = ReviewMonitorService(user_id)
                    result = run_async(service.sync_new_reviews(shop_id=shop_id))

                    if result.success:
                        data = result.data or {}
                        st.success(f"✅ 同步完成")

                        col_r1, col_r2, col_r3 = st.columns(3)
                        col_r1.metric("同步评价数", data.get("new_reviews_synced", 0))
                        col_r2.metric("高风险SKU", data.get("alert_count", 0))

                        high_risk = data.get("high_risk_skus", [])
                        if high_risk:
                            st.warning(f"⚠️ 发现 {len(high_risk)} 个高风险SKU")
                            risk_df = pd.DataFrame(high_risk)
                            st.dataframe(risk_df, width='stretch')
                    else:
                        st.error(f"❌ {result.message}")

        st.markdown("---")
        st.markdown("#### 近期评价")

        from db import execute_query
        reviews = execute_query(
            "SELECT * FROM temu_reviews WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (user_id,), fetch=True,
        ) or []

        if reviews:
            records = []
            for r in reviews:
                rating = int(r.get("rating", 5))
                stars = "⭐" * rating + "☆" * (5 - rating)
                records.append({
                    "SKU": r.get("sku", ""),
                    "评分": stars,
                    "内容": (r.get("content", "") or "")[:80] + "...",
                    "关键词": r.get("keywords", ""),
                    "时间": r.get("created_at", ""),
                })
            st.dataframe(pd.DataFrame(records), width='stretch')
        else:
            st.info("暂无评价数据")

    with tab2:
        st.markdown("#### 差评深度分析")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="analysis_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("📊 分析差评", type="primary", use_container_width=True):
                service = ReviewMonitorService(user_id)
                result = run_async(service.analyze_reviews(shop_id=shop_id))

                if result.success:
                    data = result.data or {}
                    total_bad = data.get("total_bad_reviews", 0)
                    keyword_stats = data.get("keyword_stats", {})

                    st.success(f"✅ 分析完成，共 {total_bad} 条差评")

                    if keyword_stats:
                        st.subheader("🏆 差评关键词 TOP 10")

                        kw_df = pd.DataFrame(
                            list(keyword_stats.items()),
                            columns=["关键词", "出现次数"],
                        )
                        st.dataframe(kw_df, width='stretch')

                        st.bar_chart(kw_df.set_index("关键词"))
                    else:
                        st.info("暂无差评关键词数据")
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    st.markdown("---")
    st.caption("差评监控模块 | 实时监控评价，快速定位问题SKU")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

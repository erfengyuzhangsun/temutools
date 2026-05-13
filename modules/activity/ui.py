import streamlit as st
import asyncio
import pandas as pd
from common.services_p2p3 import ActivityService


def show_page():
    st.markdown('<p class="main-header">🎯 活动报名</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">活动自动匹配 · 批量报名 · 活动状态追踪</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2 = st.tabs(["🔍 活动匹配", "📋 我的报名"])

    with tab1:
        st.markdown("#### 获取可报名活动")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🔍 获取并匹配活动", type="primary", use_container_width=True):
                service = ActivityService(user_id)
                result = asyncio.run(service.fetch_and_match(shop_id=shop_id))

                if result.success:
                    data = result.data or {}
                    activities = data.get("activities", [])

                    if activities:
                        st.success(f"✅ 找到 {len(activities)} 个可报名活动")

                        for act in activities:
                            with st.container():
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>🎯 {act.get('name', '未知活动')}</h4>
                                    <p>活动ID: {act.get('activity_id', '')}</p>
                                    <p>匹配SKU数: <strong>{act.get('count', 0)}</strong></p>
                                </div>
                                """, unsafe_allow_html=True)

                                with st.expander(f"查看匹配SKU ({act.get('count', 0)}个)"):
                                    st.write(", ".join(act.get("matched_skus", [])))

                                    if st.button(f"📋 报名此活动", key=act.get("activity_id")):
                                        sku_list = act.get("matched_skus", [])
                                        result2 = asyncio.run(
                                            service.batch_apply(
                                                shop_id=shop_id,
                                                activity_id=act.get("activity_id"),
                                                sku_list=sku_list,
                                            )
                                        )

                                        if result2.success:
                                            st.success(f"✅ 报名成功，共 {len(sku_list)} 个SKU")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {result2.message}")
                    else:
                        st.info("暂无可匹配的活动")
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab2:
        st.markdown("#### 已报名活动")

        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_activities WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,), fetch=True,
        ) or []

        if rows:
            records = []
            for r in rows:
                records.append({
                    "活动ID": r.get("activity_id", ""),
                    "状态": "✅ 已报名" if r.get("status") == "applied" else "📋 待处理",
                    "报名SKU数": len((r.get("applied_skus", "") or "").split(",")) if r.get("applied_skus") else 0,
                    "创建时间": r.get("created_at", ""),
                })
            st.dataframe(pd.DataFrame(records), width='stretch')
        else:
            st.info("暂无报名记录")

    st.markdown("---")
    st.caption("活动报名模块 | 智能匹配活动，一键批量报名")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

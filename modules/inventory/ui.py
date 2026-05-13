import streamlit as st
import asyncio
import pandas as pd
from modules.inventory.service import InventoryService


def show_page():
    st.markdown('<p class="main-header">📦 库存管理系统</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">实时库存同步 · 安全库存告警 · 补货建议 · 滞销识别</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 库存概览", "🔄 同步库存", "⚠️ 库存告警", "📊 补货建议"])

    with tab1:
        st.markdown("#### 当前库存状态")
        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            service = InventoryService(user_id)
            items = service._get_all_inventory(shop_id)

            if items:
                df = pd.DataFrame(items)
                display_cols = ["sku", "product_name", "current_stock", "safety_stock",
                                "daily_avg_sales", "lead_time_days", "status"]
                show = {c: c for c in display_cols if c in df.columns}
                st.dataframe(df[list(show.keys())].rename(columns={
                    "sku": "SKU", "product_name": "商品名称", "current_stock": "当前库存",
                    "safety_stock": "安全库存", "daily_avg_sales": "日均销量",
                    "lead_time_days": "备货天数", "status": "状态",
                }), width='stretch')

                total_stock = sum(int(i.get("current_stock", 0)) for i in items)
                low_stock = sum(1 for i in items if int(i.get("current_stock", 0)) < int(i.get("safety_stock", 0)))

                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("SKU 总数", len(items))
                col_m2.metric("总库存量", total_stock)
                col_m3.metric("库存不足 SKU", low_stock, delta_color="inverse")
            else:
                st.info("暂无库存数据，请先同步")
        else:
            st.info("暂无店铺数据")

    with tab2:
        st.markdown("#### 同步库存数据")
        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="sync_inv_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🔄 同步库存", type="primary", use_container_width=True):
                service = InventoryService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(service.sync_inventory(shop_id=shop_id))
                loop.close()

                if result.success:
                    st.success(f"✅ {result.message}")
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab3:
        st.markdown("#### 库存告警检查")
        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="alert_inv_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🔍 检查告警", type="primary", use_container_width=True):
                service = InventoryService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(service.check_inventory_alerts(shop_id=shop_id))
                loop.close()

                if result.success:
                    data = result.data or {}
                    alerts = data.get("alerts", [])
                    if alerts:
                        st.warning(f"发现 {len(alerts)} 条告警")
                        alert_data = []
                        for a in alerts:
                            type_map = {
                                "out_of_stock": "🔴 缺货",
                                "low_stock": "🟡 库存不足",
                                "slow_moving": "🔵 滞销",
                            }
                            alert_data.append({
                                "SKU": a.get("sku", ""),
                                "类型": type_map.get(a.get("type", ""), a.get("type", "")),
                                "详情": a.get("msg", ""),
                            })
                        st.dataframe(pd.DataFrame(alert_data), width='stretch')
                    else:
                        st.success("✅ 当前无库存告警")
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab4:
        st.markdown("#### 智能补货建议")
        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="replenish_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("📊 生成补货建议", type="primary", use_container_width=True):
                service = InventoryService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(
                    service.generate_replenishment_suggestions(shop_id=shop_id)
                )
                loop.close()

                if result.success:
                    data = result.data or {}
                    suggestions = data.get("suggestions", [])
                    if suggestions:
                        df = pd.DataFrame(suggestions)
                        priority_map = {"high": "🔴 高", "medium": "🟡 中", "low": "🟢 低"}
                        if "priority" in df.columns:
                            df["优先级"] = df["priority"].map(priority_map)
                        st.dataframe(df, width='stretch')

                        high_priority = sum(1 for s in suggestions if s.get("priority") == "high")
                        if high_priority > 0:
                            st.warning(f"🔴 {high_priority} 个SKU需要紧急补货")
                    else:
                        st.info("暂无补货建议")
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    st.markdown("---")
    st.caption("库存管理系统 | 智能预警，避免缺货与积压")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

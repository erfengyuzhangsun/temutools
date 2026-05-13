import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime
from modules.pricing.service import PricingService


def show_page():
    st.markdown('<p class="main-header">💰 核价自动化</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">毛利率自动判断 · 活动商品独立阈值 · 超时提醒</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2 = st.tabs(["🤖 自动核价", "📋 核价日志"])

    with tab1:
        st.markdown("#### 核价配置")

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            profit_threshold = st.slider(
                "毛利率阈值 (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.5,
                help="低于此阈值的核价通知将自动拒绝",
            )
        with col_c2:
            activity_threshold = st.slider(
                "活动商品毛利率阈值 (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5,
                help="活动商品的独立毛利率阈值",
            )

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🚀 执行自动核价", type="primary", use_container_width=True):
                service = PricingService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(service.auto_handle_pricing(shop_id=shop_id))
                loop.close()

                if result.success:
                    data = result.data or {}
                    st.success(f"✅ {result.message}")

                    if data.get("handled_count", 0) > 0:
                        results = data.get("results", [])
                        df = pd.DataFrame(results)
                        if not df.empty:
                            df["毛利率"] = df["gross_margin"].apply(lambda x: f"{x:.1f}%")
                            df["操作"] = df["action"].map({
                                "accept": "✅ 接受", "reject": "❌ 拒绝", "skip": "⏭️ 跳过",
                            })
                            df["核价ID"] = df["notice_id"]
                            st.dataframe(
                                df[["核价ID", "SKU", "操作", "供货价", "成本价", "毛利率", "原因"]],
                                width='stretch',
                            )

                    if data.get("expiring_soon"):
                        st.warning(f"⏰ {len(data['expiring_soon'])} 条核价即将过期")
                        for exp in data["expiring_soon"]:
                            st.info(f"SKU: {exp['sku']} | 过期时间: {exp['expire_at']}")
                else:
                    st.error(f"❌ 核价处理失败: {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab2:
        st.markdown("#### 核价日志查询")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="pricing_log_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            limit = st.slider("显示条数", min_value=10, max_value=100, value=50)

            if st.button("📋 查询核价日志", use_container_width=True):
                service = PricingService(user_id)
                loop = asyncio.new_event_loop()
                logs = loop.run_until_complete(service.get_pricing_logs(shop_id=shop_id, limit=limit))
                loop.close()

                if logs:
                    records = []
                    for log in logs:
                        action_map = {
                            "accept": "✅ 接受", "reject": "❌ 拒绝",
                            "skip": "⏭️ 跳过", "pending": "⏳ 待处理",
                        }
                        records.append({
                            "时间": log.handled_at.strftime("%Y-%m-%d %H:%M:%S") if log.handled_at else "-",
                            "SKU": log.sku,
                            "操作": action_map.get(log.action, log.action),
                            "供货价": f"¥{log.supply_price:.2f}",
                            "成本价": f"¥{log.cost_price:.2f}",
                            "毛利率": f"{log.gross_margin:.1f}%",
                            "活动商品": "是" if log.is_activity else "否",
                            "原因": log.reason,
                        })
                    st.dataframe(pd.DataFrame(records), width='stretch')
                else:
                    st.info("暂无核价日志")
        else:
            st.info("暂无店铺数据")

    st.markdown("---")
    st.caption("核价自动化模块 | 智能判断毛利率，自动处理核价通知")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

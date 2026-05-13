import streamlit as st
import asyncio
import pandas as pd
from modules.dashboard.service import DashboardService


def show_page():
    st.markdown('<p class="main-header">📊 多店铺总控大屏</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">全局总看板 · 告警聚合 · 多店铺数据汇总</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2 = st.tabs(["🏠 全局总览", "🚨 告警中心"])

    with tab1:
        service = DashboardService(user_id)
        result = asyncio.run(service.get_overview())

        if result.success:
            data = result.data or {}
            overview = data.get("overview", {})

            if overview:
                col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
                col_sum1.metric("店铺总数", overview.get("shop_count", 0))
                col_sum2.metric("总利润", f"¥{overview.get('total_profit', 0):,.2f}")
                col_sum3.metric("总收入", f"¥{overview.get('total_revenue', 0):,.2f}")
                col_sum4.metric("总告警", overview.get("total_alerts", 0))

                st.markdown("---")
                st.markdown("#### 告警分类统计")

                col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                with col_a1:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: #ffc107;">
                        <h6>⏰ 核价待处理</h6>
                        <p style="font-size: 1.8rem; font-weight: bold; color: #ffc107;">
                            {overview.get('pricing_pending', 0)}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_a2:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: #dc3545;">
                        <h6>📦 库存告警</h6>
                        <p style="font-size: 1.8rem; font-weight: bold; color: #dc3545;">
                            {overview.get('inventory_alerts', 0)}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_a3:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: #fd7e14;">
                        <h6>⚠️ 风控告警</h6>
                        <p style="font-size: 1.8rem; font-weight: bold; color: #fd7e14;">
                            {overview.get('risk_warnings', 0)}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_a4:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: #6f42c1;">
                        <h6>💬 差评告警</h6>
                        <p style="font-size: 1.8rem; font-weight: bold; color: #6f42c1;">
                            {overview.get('review_alerts', 0)}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                shop_details = overview.get("shop_details", [])
                if shop_details:
                    st.markdown("---")
                    st.markdown("#### 各店铺详情")

                    for shop in shop_details:
                        with st.container():
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🏪 {shop.get('shop_name', '未知店铺')}</h4>
                                <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                                    <span>📈 利润: <strong>¥{shop.get('profit', 0):,.2f}</strong></span>
                                    <span>💰 收入: <strong>¥{shop.get('revenue', 0):,.2f}</strong></span>
                                    <span>⏰ 核价: <strong>{shop.get('pricing_pending', 0)}</strong></span>
                                    <span>📦 库存: <strong>{shop.get('inventory_alerts', 0)}</strong></span>
                                    <span>⚠️ 风险: <strong>{shop.get('risk_warnings', 0)}</strong></span>
                                    <span>💬 差评: <strong>{shop.get('review_alerts', 0)}</strong></span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.error(f"❌ 获取总览数据失败: {result.message}")

    with tab2:
        st.markdown("#### 全局告警中心")

        service = DashboardService(user_id)
        result = asyncio.run(service.get_all_alerts())

        if result.success:
            data = result.data or {}
            alerts = data.get("alerts", [])

            if alerts:
                severity_map = {"high": "🔴 高", "medium": "🟡 中", "low": "🟢 低"}

                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    severity_filter = st.multiselect(
                        "按严重程度筛选",
                        options=["high", "medium", "low"],
                        default=["high", "medium"],
                        format_func=lambda x: severity_map.get(x, x),
                    )
                with col_f2:
                    type_filter = st.multiselect(
                        "按类型筛选",
                        options=list(set(a.get("type", "") for a in alerts)),
                    )

                filtered = alerts
                if severity_filter:
                    filtered = [a for a in filtered if a.get("severity") in severity_filter]
                if type_filter:
                    filtered = [a for a in filtered if a.get("type") in type_filter]

                alert_df = pd.DataFrame(filtered)
                if not alert_df.empty:
                    alert_df["严重程度"] = alert_df["severity"].map(severity_map)
                    st.dataframe(
                        alert_df[["shop", "type", "严重程度", "msg"]].rename(columns={
                            "shop": "店铺", "type": "类型", "msg": "详情",
                        }),
                        width='stretch',
                    )
                    st.info(f"共 {len(filtered)} 条告警")
                else:
                    st.info("无匹配的告警")
            else:
                st.success("✅ 当前无告警")
        else:
            st.error(f"❌ 获取告警失败: {result.message}")

    st.markdown("---")
    st.caption("多店铺统一总控大屏 | 一站式管理所有店铺运营状态")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

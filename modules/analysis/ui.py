import streamlit as st
import pandas as pd
from modules.analysis.service import AnalysisService
from common.async_runner import run as run_async


def show_page():
    st.markdown('<p class="main-header">📊 数据分析与预警</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">店铺指标采集 · 转化率/退货率告警 · 自动报表</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2, tab3 = st.tabs(["📈 指标采集", "🚨 告警检查", "📄 数据报表"])

    with tab1:
        st.markdown("#### 采集店铺运营指标")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("📥 采集指标", type="primary", use_container_width=True):
                service = AnalysisService(user_id)
                result = run_async(service.collect_metrics(shop_id=shop_id))

                if result.success:
                    data = result.data or {}
                    metrics = data.get("metrics", {})
                    if metrics:
                        st.success("✅ 指标采集完成")

                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        col_m1.metric("曝光量", metrics.get("impressions", 0))
                        col_m2.metric("点击率", f"{metrics.get('click_rate', 0):.2f}%")
                        col_m3.metric("转化率", f"{metrics.get('conversion_rate', 0):.2f}%")
                        col_m4.metric("退货率", f"{metrics.get('return_rate', 0):.2f}%")

                        col_m5, col_m6, col_m7 = st.columns(3)
                        col_m5.metric("总销售额", f"¥{metrics.get('total_sales', 0):,.2f}")
                        col_m6.metric("总订单数", metrics.get("total_orders", 0))
                        col_m7.metric("差评率", f"{metrics.get('negative_review_rate', 0):.2f}%")
                else:
                    st.error(f"❌ 采集失败: {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab2:
        st.markdown("#### 运营指标告警检查")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            conv_threshold = st.slider(
                "转化率告警阈值 (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5,
            )
        with col_t2:
            ret_threshold = st.slider(
                "退货率告警阈值 (%)", min_value=0.0, max_value=50.0, value=15.0, step=0.5,
            )

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="alert_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🔍 检查告警", type="primary", use_container_width=True):
                service = AnalysisService(user_id)
                result = run_async(service.check_metric_alerts(shop_id=shop_id))

                if result.success:
                    data = result.data or {}
                    alerts = data.get("alerts", [])
                    if alerts:
                        st.warning(f"⚠️ 发现 {len(alerts)} 条告警")
                        for alert in alerts:
                            alert_type = alert.get("type", "")
                            level = alert.get("level", "info")
                            value = alert.get("value", 0)
                            threshold = alert.get("threshold", 0)
                            suggestion = alert.get("suggestion", "")

                            if alert_type == "conversion_rate":
                                st.error(f"🔴 转化率过低: {value:.2f}% (阈值: {threshold}%)")
                            elif alert_type == "return_rate":
                                st.error(f"🔴 退货率过高: {value:.2f}% (阈值: {threshold}%)")

                            st.info(f"💡 建议: {suggestion}")
                    else:
                        st.success("✅ 当前指标均在安全范围内")
                else:
                    st.error(f"❌ 检查失败: {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab3:
        st.markdown("#### 运营数据报表")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="report_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            report_type = st.selectbox("报表类型", ["daily", "weekly", "monthly"])

            if st.button("📄 生成报表", type="primary", use_container_width=True):
                service = AnalysisService(user_id)
                result = run_async(
                    service.generate_report(shop_id=shop_id, report_type=report_type)
                )

                if result.success:
                    data = result.data or {}
                    report = data.get("report", {})
                    if report:
                        st.success("✅ 报表生成成功")

                        metrics = report.get("metrics", {})
                        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                        col_r1.metric("总销售额", f"¥{metrics.get('total_sales', 0):,.2f}")
                        col_r2.metric("总订单数", metrics.get("total_orders", 0))
                        col_r3.metric("平均转化率", f"{metrics.get('avg_conversion', 0):.2f}%")
                        col_r4.metric("平均退货率", f"{metrics.get('avg_return_rate', 0):.2f}%")

                        trends = report.get("trends", {})
                        if trends.get("dates"):
                            trend_df = pd.DataFrame({
                                "日期": trends["dates"],
                                "曝光量": trends.get("impressions", []),
                                "转化率": trends.get("conversion_rate", []),
                                "退货率": trends.get("return_rate", []),
                            })
                            st.subheader("📈 趋势数据")
                            st.dataframe(trend_df, width='stretch')
                else:
                    st.error(f"❌ 报表生成失败: {result.message}")
        else:
            st.info("暂无店铺数据")

    st.markdown("---")
    st.caption("数据自动分析与预警模块 | 智能监控店铺运营健康度")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

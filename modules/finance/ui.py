import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime
from modules.finance.service import FinanceService


def show_page():
    st.markdown('<p class="main-header">💳 财务结算对账</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">结算同步 · 月度汇总 · 回款预估 · 差异对账</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2, tab3, tab4 = st.tabs(["📥 结算同步", "📊 月度汇总", "🔮 回款预估", "📋 对账管理"])

    with tab1:
        st.markdown("#### 同步结算数据")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🔄 同步结算", type="primary", use_container_width=True):
                service = FinanceService(user_id)
                result = asyncio.run(service.sync_settlement(shop_id=shop_id))

                if result.success:
                    data = result.data or {}
                    st.success(f"✅ 同步完成，共 {data.get('synced_count', 0)} 条结算记录")
                else:
                    st.error(f"❌ 同步失败: {result.message}")
        else:
            st.info("暂无店铺数据")

        st.markdown("---")
        st.markdown("#### 近期结算记录")
        from db import execute_query

        rows = execute_query(
            "SELECT * FROM temu_settlements WHERE user_id = ? ORDER BY period_end DESC LIMIT 10",
            (user_id,), fetch=True,
        ) or []

        if rows:
            records = []
            for r in rows:
                records.append({
                    "结算周期": f"{r.get('period_start', '')} ~ {r.get('period_end', '')}",
                    "总收入": f"¥{float(r.get('total_revenue', 0)):,.2f}",
                    "总扣费": f"¥{float(r.get('total_deductions', 0)):,.2f}",
                    "净收入": f"¥{float(r.get('net_payout', 0)):,.2f}",
                    "状态": "✅ 已结算" if r.get("status") == "settled" else "⏳ 处理中",
                    "结算日期": r.get("settlement_date", ""),
                })
            st.dataframe(pd.DataFrame(records), width='stretch')
        else:
            st.info("暂无结算数据")

    with tab2:
        st.markdown("#### 月度利润汇总")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="monthly_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            month = st.text_input("月份 (YYYY-MM)", value=datetime.now().strftime("%Y-%m"))

            if st.button("📊 查看月度汇总", type="primary", use_container_width=True):
                service = FinanceService(user_id)
                result = asyncio.run(
                    service.get_monthly_profit_summary(shop_id=shop_id, month=month)
                )

                if result.success:
                    data = result.data or {}
                    summary = data.get("summary", {})
                    if summary:
                        st.success(f"✅ {month} 月度汇总")

                        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                        col_s1.metric("总收入", f"¥{summary.get('total_revenue', 0):,.2f}")
                        col_s2.metric("总成本", f"¥{summary.get('total_cost', 0):,.2f}")
                        col_s3.metric("总利润", f"¥{summary.get('total_profit', 0):,.2f}")
                        col_s4.metric("利润率", f"{summary.get('profit_rate', 0):.2f}%")

                        details = summary.get("shop_details", [])
                        if details:
                            st.dataframe(pd.DataFrame(details), width='stretch')
                else:
                    st.error(f"❌ 查询失败: {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab3:
        st.markdown("#### 回款预估")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="payout_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🔮 预估下期回款", type="primary", use_container_width=True):
                service = FinanceService(user_id)
                result = asyncio.run(
                    service.predict_next_payout(shop_id=shop_id)
                )

                if result.success:
                    data = result.data or {}
                    predicted = data.get("predicted", 0)
                    if predicted > 0:
                        st.success(f"✅ 预估完成")
                        col_p1, col_p2, col_p3 = st.columns(3)
                        col_p1.metric("预计回款", f"¥{predicted:,.2f}")
                        col_p2.metric("基于期数", data.get("based_on", 0))
                        col_p3.metric("平均收入", f"¥{data.get('avg_revenue', 0):,.2f}")

                        st.info(f"基于过去 {data.get('based_on', 0)} 期结算数据预测")
                    else:
                        st.info(data.get("message", "暂无足够历史数据"))
                else:
                    st.error(f"❌ 预估失败: {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab4:
        st.markdown("#### 结算对账")

        from db import execute_query
        settlements = execute_query(
            "SELECT settlement_id, period_start, period_end, net_payout, status "
            "FROM temu_settlements WHERE user_id = ? AND status = 'settled' ORDER BY period_end DESC LIMIT 20",
            (user_id,), fetch=True,
        ) or []

        if settlements:
            settlement_options = {
                f"{s['period_start']} ~ {s['period_end']} (¥{float(s['net_payout']):,.2f})": s["settlement_id"]
                for s in settlements
            }
            selected_settlement = st.selectbox("选择结算单", list(settlement_options.keys()))
            settlement_id = settlement_options[selected_settlement]

            shops = _get_user_shops(user_id)
            if shops:
                selected_shop = st.selectbox(
                    "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                    key="recon_shop"
                )
                shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

                if st.button("📋 执行对账", type="primary", use_container_width=True):
                    service = FinanceService(user_id)
                    result = asyncio.run(
                        service.reconcile(shop_id=shop_id, settlement_id=settlement_id)
                    )

                    if result.success:
                        data = result.data or {}
                        st.success(f"✅ 对账完成")

                        status = data.get("status", "")
                        if status == "matched":
                            st.success("✅ 账目一致，无差异")
                        else:
                            st.warning("⚠️ 存在差异")

                        col_r1, col_r2, col_r3 = st.columns(3)
                        col_r1.metric("预期金额", f"¥{data.get('expected', 0):,.2f}")
                        col_r2.metric("实际金额", f"¥{data.get('actual', 0):,.2f}")
                        col_r3.metric("差异", f"¥{data.get('difference', 0):,.2f}")
                    else:
                        st.error(f"❌ 对账失败: {result.message}")
        else:
            st.info("暂无已结算数据可供对账")

    st.markdown("---")
    st.caption("财务结算对账模块 | 自动同步，智能对账，精准回款预估")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

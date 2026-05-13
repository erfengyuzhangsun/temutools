import streamlit as st
import asyncio
import pandas as pd
from modules.pricing_adj.service import PricingAdjustmentService
from modules.pricing_adj.config import MODULE_CONFIG


def show_page():
    st.markdown('<p class="main-header">🏷️ 智能定价调价</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">竞品降价跟调 · 保本毛利锁 · 活动价切换</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2 = st.tabs(["🤖 自动调价", "📊 调价记录"])

    with tab1:
        st.markdown("#### 调价配置")

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            min_margin = st.slider(
                "最低保本毛利率 (%)",
                min_value=0.0, max_value=50.0,
                value=MODULE_CONFIG["min_gross_margin"]["default"],
                step=0.5,
            )
        with col_c2:
            max_daily = st.number_input(
                "每日最大调价次数",
                min_value=1, max_value=50,
                value=MODULE_CONFIG["max_daily_adjustments"]["default"],
            )
        with col_c3:
            follow_ratio = st.slider(
                "竞品降价跟进比例",
                min_value=0.0, max_value=1.0,
                value=MODULE_CONFIG["competitor_price_drop_ratio"]["default"],
                step=0.05,
                help="0.5表示跟进竞品降价幅度的50%",
            )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sku = st.text_input("SKU 编码", placeholder="输入要调价的SKU编码")

        shops = _get_user_shops(user_id)
        if shops:
            with col_s2:
                selected_shop = st.selectbox(
                    "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🚀 自动调价", type="primary", use_container_width=True):
                    if not sku:
                        st.error("请输入SKU编码")
                    else:
                        service = PricingAdjustmentService(user_id)
                        result = asyncio.run(
                            service.auto_adjust_price(shop_id=shop_id, sku=sku)
                        )

                        if result.success:
                            data = result.data or {}
                            if data.get("new_price") and data.get("old_price"):
                                old_p = data["old_price"]
                                new_p = data["new_price"]
                                change = ((new_p - old_p) / old_p) * 100 if old_p else 0
                                st.success(f"✅ 调价完成")
                                st.metric(
                                    f"SKU: {data.get('sku', sku)}",
                                    f"¥{new_p:.2f}",
                                    delta=f"{change:+.1f}%",
                                )
                                if data.get("reason"):
                                    st.info(f"原因: {data['reason']}")
                            else:
                                st.info(result.message)
                        else:
                            st.error(f"❌ {result.message}")

            with col_b2:
                st.markdown("##### 活动价切换")
                activity_price = st.number_input("活动价格", min_value=0.0, step=0.5)

                if st.button("🏷️ 切换活动价", use_container_width=True):
                    if not sku:
                        st.error("请输入SKU编码")
                    elif activity_price <= 0:
                        st.error("请输入有效活动价格")
                    else:
                        service = PricingAdjustmentService(user_id)
                        result = asyncio.run(
                            service.adjust_for_activity(shop_id=shop_id, sku=sku, activity_price=activity_price)
                        )

                        if result.success:
                            data = result.data or {}
                            st.success(f"✅ 活动价已生效")
                            if data.get("old_price") and data.get("new_price"):
                                st.info(f"原价: ¥{data['old_price']:.2f} → 活动价: ¥{data['new_price']:.2f}")
                        else:
                            st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab2:
        st.markdown("#### 调价历史记录")
        from db import execute_query

        rows = execute_query(
            "SELECT * FROM temu_price_adjustments WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
            (user_id,), fetch=True,
        ) or []

        if rows:
            records = []
            for r in rows:
                records.append({
                    "SKU": r.get("sku", ""),
                    "原价": f"¥{float(r.get('old_price', 0)):.2f}",
                    "新价": f"¥{float(r.get('new_price', 0)):.2f}",
                    "原因": r.get("reason", ""),
                    "时间": r.get("created_at", ""),
                })
            st.dataframe(pd.DataFrame(records), width='stretch')
        else:
            st.info("暂无调价记录")

    st.markdown("---")
    st.caption("智能定价调价模块 | 竞品监控，自动跟调，保本锁利")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

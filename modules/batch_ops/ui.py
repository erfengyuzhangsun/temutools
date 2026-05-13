import streamlit as st
import asyncio
import pandas as pd
from common.services_p2p3 import BatchOpsService


def show_page():
    st.markdown('<p class="main-header">📋 批量运营</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">批量下架 · 批量操作 · 运营效率提升</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    st.markdown("#### 批量下架商品")

    shops = _get_user_shops(user_id)
    if shops:
        selected_shop = st.selectbox(
            "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
        )
        shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

        st.markdown("---")
        st.markdown("##### 从以下方式选择要下架的SKU")

        input_method = st.radio("选择方式", ["手动输入SKU", "从现有商品选择"])

        sku_list = []

        if input_method == "手动输入SKU":
            sku_input = st.text_area(
                "输入SKU列表（每行一个SKU）",
                placeholder="SKU001\nSKU002\nSKU003",
                height=150,
            )
            if sku_input.strip():
                sku_list = [s.strip() for s in sku_input.split("\n") if s.strip()]
        else:
            from db import execute_query
            products = execute_query(
                "SELECT DISTINCT sku, product_name FROM temu_sync_orders "
                "WHERE user_id = ? AND shop_id = ? AND status != 'offline' LIMIT 50",
                (user_id, shop_id), fetch=True,
            ) or []

            if products:
                selected_skus = st.multiselect(
                    "选择要下架的商品",
                    options=[f"{p['sku']} - {p.get('product_name', '')}" for p in products],
                )
                sku_list = [s.split(" - ")[0] for s in selected_skus]
            else:
                st.info("暂无可用商品数据")

        if sku_list:
            st.info(f"已选择 {len(sku_list)} 个SKU")

            st.markdown("---")
            st.warning("⚠️ 批量下架操作不可撤销，请确认后再执行")

            confirm = st.checkbox("我确认要下架以上商品", value=False)

            col_b1, col_b2, col_b3 = st.columns([1, 1, 2])
            with col_b1:
                if st.button("📋 执行批量下架", type="primary", use_container_width=True, disabled=not confirm):
                    service = BatchOpsService(user_id)
                    result = asyncio.run(
                        service.batch_offline(shop_id=shop_id, sku_list=sku_list)
                    )

                    if result.success:
                        data = result.data or {}
                        st.success(f"✅ 批量下架完成")

                        col_r1, col_r2, col_r3 = st.columns(3)
                        col_r1.metric("成功", data.get("success", 0))
                        col_r2.metric("失败", data.get("failed", 0))
                        col_r3.metric("总数", data.get("total", 0))

                        if data.get("results"):
                            st.dataframe(pd.DataFrame({
                                "已下架SKU": data["results"],
                            }), width='stretch')
                    else:
                        st.error(f"❌ 操作失败: {result.message}")
    else:
        st.info("暂无店铺数据")

    st.markdown("---")
    st.caption("批量运营模块 | 高效批量管理商品，提升运营效率")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

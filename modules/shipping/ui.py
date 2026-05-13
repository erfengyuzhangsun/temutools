import streamlit as st
import asyncio
import pandas as pd
from common.services_p2p3 import ShippingService


def show_page():
    st.markdown('<p class="main-header">📦 标签与发货</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">面单标签生成 · 发货单管理 · 批量打印</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2 = st.tabs(["🏷️ 生成标签", "📋 发货单管理"])

    with tab1:
        st.markdown("#### 生成商品标签")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            sku_input = st.text_area(
                "输入SKU列表（每行一个SKU）",
                placeholder="SKU001\nSKU002\nSKU003",
                height=120,
            )

            if st.button("🏷️ 生成标签", type="primary", use_container_width=True):
                if not sku_input.strip():
                    st.error("请输入至少一个SKU")
                else:
                    sku_list = [s.strip() for s in sku_input.split("\n") if s.strip()]
                    service = ShippingService(user_id)
                    loop = asyncio.new_event_loop()
                    result = loop.run_until_complete(
                        service.generate_labels(shop_id=shop_id, sku_list=sku_list)
                    )
                    loop.close()

                    if result.success:
                        data = result.data or {}
                        labels = data.get("labels", [])
                        st.success(f"✅ 成功生成 {len(labels)} 张标签")

                        if labels:
                            label_df = pd.DataFrame(labels)
                            st.dataframe(label_df, width='stretch')

                            csv = label_df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                "📥 下载标签数据 (CSV)",
                                data=csv,
                                file_name="shipping_labels.csv",
                                mime="text/csv",
                            )
                    else:
                        st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

        st.markdown("---")
        st.markdown("#### 已生成标签")
        from db import execute_query
        labels = execute_query(
            "SELECT * FROM temu_shipping_labels WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (user_id,), fetch=True,
        ) or []

        if labels:
            label_records = []
            for l in labels:
                label_records.append({
                    "SKU": l.get("sku", ""),
                    "状态": "✅ 就绪" if l.get("status") == "ready" else "📋 已打印",
                    "生成时间": l.get("created_at", ""),
                })
            st.dataframe(pd.DataFrame(label_records), width='stretch')
        else:
            st.info("暂无标签数据")

    with tab2:
        st.markdown("#### 生成发货单")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="manifest_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            order_input = st.text_area(
                "输入订单ID列表（每行一个）",
                placeholder="ORD001\nORD002\nORD003",
                height=120,
            )

            if st.button("📋 生成发货单", type="primary", use_container_width=True):
                if not order_input.strip():
                    st.error("请输入至少一个订单ID")
                else:
                    order_ids = [o.strip() for o in order_input.split("\n") if o.strip()]
                    service = ShippingService(user_id)
                    loop = asyncio.new_event_loop()
                    result = loop.run_until_complete(
                        service.generate_manifest(shop_id=shop_id, order_ids=order_ids)
                    )
                    loop.close()

                    if result.success:
                        data = result.data or {}
                        manifest = data.get("manifest", {})
                        st.success(f"✅ 发货单生成成功，共 {len(order_ids)} 单")
                        st.json(manifest)
                    else:
                        st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    st.markdown("---")
    st.caption("标签与发货模块 | 高效生成面单标签，批量管理发货单")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

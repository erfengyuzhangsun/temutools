import streamlit as st
import pandas as pd
import asyncio
from common.services_p2p3 import SupplierService
from common.async_runner import run as run_async


def show_page():
    st.markdown('<p class="main-header">🏭 供应商管理</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">供应商档案 · 价格监控 · 比价采购</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2, tab3 = st.tabs(["📋 供应商列表", "➕ 添加供应商", "🔍 比价采购"])

    with tab1:
        st.markdown("#### 已注册供应商")

        from db import execute_query
        suppliers = execute_query(
            "SELECT * FROM temu_suppliers WHERE user_id = ?",
            (user_id,), fetch=True,
        ) or []

        if suppliers:
            records = []
            for s in suppliers:
                records.append({
                    "ID": s.get("supplier_id", ""),
                    "名称": s.get("name", ""),
                    "联系人": s.get("contact", ""),
                    "电话": s.get("phone", ""),
                    "主营类目": s.get("main_category", ""),
                })
            st.dataframe(pd.DataFrame(records), width='stretch')

            st.markdown("---")
            st.markdown("#### 供应商价格变动监控")

            selected_supplier = st.selectbox(
                "选择供应商查看价格变动",
                options=[s["name"] for s in suppliers],
            )
            supplier_id = next(
                (s["supplier_id"] for s in suppliers if s["name"] == selected_supplier),
                None,
            )

            if st.button("📊 查看价格变动", use_container_width=True):
                service = SupplierService(user_id)
                result = run_async(
                    service.check_price_changes(supplier_id=supplier_id)
                )

                if result.success:
                    data = result.data or {}
                    changes = data.get("changes", [])
                    if changes:
                        st.warning(f"⚠️ 发现 {len(changes)} 项价格变动")
                        st.dataframe(pd.DataFrame(changes), width='stretch')
                    else:
                        st.success("✅ 近期无价格变动")
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.info("暂无供应商，请在「添加供应商」中注册")

    with tab2:
        st.markdown("#### 注册新供应商")

        with st.form("add_supplier_form"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                name = st.text_input("供应商名称 *", placeholder="例如：某某工厂")
                contact = st.text_input("联系人", placeholder="姓名")
            with col_f2:
                phone = st.text_input("联系电话", placeholder="手机号")
                category = st.text_input("主营类目", placeholder="例如：家居百货")

            submitted = st.form_submit_button("➕ 添加供应商", type="primary", use_container_width=True)

            if submitted:
                if not name.strip():
                    st.error("❌ 请填写供应商名称（标 * 为必填项）")
                else:
                    try:
                        service = SupplierService(user_id)
                        result = service.add_supplier(
                            name=name, contact=contact,
                            phone=phone, category=category,
                        )

                        if result.success:
                            st.success(f"✅ 供应商「{name}」添加成功！欢迎合作 🎉")
                            st.info("💡 可继续添加下一个供应商")
                            if not st.session_state.get('_rerun_pending', False):
                                st.session_state['_rerun_pending'] = True
                                st.rerun()
                        else:
                            st.error(f"❌ {result.message}")
                    except Exception as e:
                        err_msg = str(e).lower()
                        if "unique" in err_msg or "integrity" in err_msg or "已存在" in err_msg:
                            st.error(f"❌ 该供应商名称「{name}」已注册，请修改后重试")
                        else:
                            st.error("❌ 添加失败，请稍后重试或联系管理员")

    with tab3:
        st.markdown("#### 供应商比价")

        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            sku = st.text_input("输入SKU编码", placeholder="例如：SKU001")
        with col_s2:
            st.markdown("##### ")
            st.markdown("##### ")

        if st.button("🔍 比价", type="primary", use_container_width=True):
            if not sku.strip():
                st.error("请输入SKU编码")
            else:
                service = SupplierService(user_id)
                result = service.compare_prices(sku)

                if result.success:
                    data = result.data or {}
                    suppliers = data.get("suppliers", [])

                    if suppliers:
                        st.success(f"✅ 共找到 {len(suppliers)} 个供应商报价")

                        df = pd.DataFrame(suppliers)
                        st.dataframe(df, width='stretch')

                        best_supplier = data.get("best_supplier", "")
                        best_price = data.get("best_price", 0)
                        st.markdown(f"""
                        <div class="metric-card" style="border-left-color: #28a745;">
                            <h4>🏆 最优报价</h4>
                            <p style="font-size: 1.5rem; font-weight: bold; color: #28a745;">
                                {best_supplier} - ¥{best_price:.2f}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("未找到该SKU的供应商报价")
                else:
                    st.error(f"❌ {result.message}")

    st.markdown("---")
    st.caption("供应商管理模块 | 建立供应商库，智能比价采购")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

import streamlit as st
import asyncio
import pandas as pd
from common.services_p2p3 import RiskInspectionService


def show_page():
    st.markdown('<p class="main-header">🔍 风控体检</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">敏感词检测 · 合规检查 · 风险评分报告</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2, tab3 = st.tabs(["🔍 全面体检", "📊 体检报告", "⚙️ 敏感词管理"])

    with tab1:
        st.markdown("#### 执行全SKU风控体检")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🔍 开始体检", type="primary", use_container_width=True):
                service = RiskInspectionService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(service.inspect_all_skus(shop_id=shop_id))
                loop.close()

                if result.success:
                    data = result.data or {}
                    violations = data.get("violations", [])
                    total_skus = data.get("total_skus", 0)

                    st.success(f"✅ 体检完成，共检查 {total_skus} 个SKU")

                    if violations:
                        st.warning(f"⚠️ 发现 {len(violations)} 项风险")

                        df = pd.DataFrame(violations)
                        st.dataframe(df, width='stretch')

                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            "📥 导出风险报告 (CSV)",
                            data=csv,
                            file_name="risk_violations.csv",
                            mime="text/csv",
                        )
                    else:
                        st.success("✅ 所有SKU合规，无风险")
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab2:
        st.markdown("#### 风控合规报告")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
                key="report_shop"
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("📊 生成报告", type="primary", use_container_width=True):
                service = RiskInspectionService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(service.generate_report(shop_id=shop_id))
                loop.close()

                if result.success:
                    data = result.data or {}
                    report = data.get("report", {})
                    if report:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 2rem;">
                            <div class="health-score-circle" style="background: linear-gradient(135deg, 
                                {'#28a745' if report.get('compliance_score', 0) >= 80 else '#ffc107' if report.get('compliance_score', 0) >= 60 else '#dc3545'}20 0%, 
                                {'#28a745' if report.get('compliance_score', 0) >= 80 else '#ffc107' if report.get('compliance_score', 0) >= 60 else '#dc3545'}40 100%); 
                                color: {'#28a745' if report.get('compliance_score', 0) >= 80 else '#ffc107' if report.get('compliance_score', 0) >= 60 else '#dc3545'};">
                                <div>
                                    <div style="font-size: 3rem; font-weight: bold;">{report.get('compliance_score', 0)}</div>
                                    <div style="font-size: 0.9rem;">合规分</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col_r1, col_r2 = st.columns(2)
                        col_r1.metric("总SKU数", report.get("total_skus", 0))
                        col_r2.metric("违规数", report.get("violations", 0))
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.info("暂无店铺数据")

    with tab3:
        st.markdown("#### 敏感词管理")

        from db import execute_query
        words = execute_query(
            "SELECT * FROM temu_sensitive_words WHERE user_id = ?",
            (user_id,), fetch=True,
        ) or []

        if words:
            st.dataframe(pd.DataFrame(words), width='stretch')
        else:
            st.info("暂无敏感词，建议添加常见违规词")

        with st.form("add_word_form"):
            new_word = st.text_input("添加敏感词", placeholder="例如：免费、第一、最")
            if st.form_submit_button("➕ 添加", use_container_width=True):
                if new_word.strip():
                    execute_query(
                        "INSERT INTO temu_sensitive_words (user_id, word) VALUES (?, ?)",
                        (user_id, new_word.strip()),
                    )
                    st.success(f"✅ 已添加: {new_word}")
                    st.rerun()

    st.markdown("---")
    st.caption("风控体检模块 | 自动检测SKU合规风险，守护店铺安全")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

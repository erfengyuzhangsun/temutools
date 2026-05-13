import streamlit as st
import asyncio
import pandas as pd
from common.services_p2p3 import MessageService


def show_page():
    st.markdown('<p class="main-header">💬 消息与售后</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">平台消息同步 · 售后模板管理 · 智能优先级标记</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2 = st.tabs(["📨 消息同步", "📝 回复模板"])

    with tab1:
        st.markdown("#### 同步平台消息")

        shops = _get_user_shops(user_id)
        if shops:
            selected_shop = st.selectbox(
                "选择店铺", {s["shop_name"]: s["shop_id"] for s in shops}.keys(),
            )
            shop_id = {s["shop_name"]: s["shop_id"] for s in shops}[selected_shop]

            if st.button("🔄 同步消息", type="primary", use_container_width=True):
                service = MessageService(user_id)
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(service.sync_messages(shop_id=shop_id))
                loop.close()

                if result.success:
                    data = result.data or {}
                    st.success(f"✅ 同步完成，共 {data.get('synced', 0)} 条消息")
                else:
                    st.error(f"❌ {result.message}")

        st.markdown("---")
        st.markdown("#### 最近消息")

        from db import execute_query
        rows = execute_query(
            "SELECT * FROM temu_messages WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (user_id,), fetch=True,
        ) or []

        if rows:
            records = []
            for r in rows:
                priority_emoji = {"high": "🔴", "normal": "🟢", "low": "⚪"}
                records.append({
                    "优先级": priority_emoji.get(r.get("priority", "normal"), "⚪"),
                    "主题": r.get("topic", ""),
                    "内容": (r.get("content", "") or "")[:60] + "...",
                    "类别": r.get("category", ""),
                    "时间": r.get("created_at", ""),
                })
            st.dataframe(pd.DataFrame(records), width='stretch')
        else:
            st.info("暂无消息数据")

    with tab2:
        st.markdown("#### 回复模板管理")

        service = MessageService(user_id)
        templates = service.get_templates()

        category = st.text_input("按类别筛选（留空显示全部）", "")
        if category:
            templates = service.get_templates(category=category)

        if templates:
            for t in templates:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h6>{t.get('title', '未命名模板')}</h6>
                        <p>{t.get('content', '')[:100]}{'...' if len(t.get('content', '')) > 100 else ''}</p>
                        <small>类别: {t.get('category', '通用')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("暂无回复模板")

        st.markdown("---")
        with st.expander("➕ 新建回复模板"):
            with st.form("new_template_form"):
                title = st.text_input("模板标题")
                content = st.text_area("模板内容")
                tmpl_category = st.text_input("模板类别", value="售后")
                if st.form_submit_button("创建模板", use_container_width=True):
                    from db import execute_query
                    execute_query(
                        "INSERT INTO temu_reply_templates (user_id, title, content, category) VALUES (?, ?, ?, ?)",
                        (user_id, title, content, tmpl_category),
                    )
                    st.success("✅ 模板创建成功")
                    st.rerun()

    st.markdown("---")
    st.caption("消息与售后模块 | 及时处理平台消息，提高客服效率")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

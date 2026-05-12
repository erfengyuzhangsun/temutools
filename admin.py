import streamlit as st
import pandas as pd
from datetime import datetime, date
from db import (
    list_all_users, add_user, extend_user_expiry, toggle_user_active,
    delete_expired_user_data, export_user_data, get_user_history_stats,
    get_user_history_risks
)
from auth import get_current_user, get_user_id

ADMIN_PASSWORD = "admin888"


def is_admin() -> bool:
    user = get_current_user()
    if not user:
        return False
    return st.session_state.get('is_admin', False)


def show_admin_login():
    st.markdown("""
    <style>
        .admin-section {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='admin-section'><h3>🔐 管理员入口</h3><p>请输入管理员密码以管理用户</p></div>", unsafe_allow_html=True)

    admin_pwd = st.text_input("管理员密码", type="password", key="admin_pwd_input")
    if st.button("验证管理员身份", use_container_width=True, type="primary"):
        if admin_pwd == ADMIN_PASSWORD:
            st.session_state['is_admin'] = True
            st.success("管理员验证通过！")
            st.rerun()
        else:
            st.error("管理员密码错误")


def show_admin_panel():
    if not is_admin():
        show_admin_login()
        return

    st.markdown("""
    <style>
        .admin-header {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            padding: 1rem 1.5rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .stat-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div class='admin-header'><h2>⚙️ 管理员控制台</h2><p>用户管理与系统维护</p></div>", unsafe_allow_html=True)
    with col2:
        if st.button("🚪 退出管理", use_container_width=True):
            st.session_state['is_admin'] = False
            st.rerun()

    tab_add, tab_list, tab_maintain = st.tabs(["➕ 添加用户", "📋 用户列表", "🔧 系统维护"])

    with tab_add:
        st.markdown("### 添加新付费用户")
        with st.form("add_user_form"):
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                wechat = st.text_input("微信昵称 *", placeholder="用户微信昵称")
                plan_type = st.selectbox(
                    "套餐类型 *",
                    options=[("basic", "基础版 ¥39.9/月"), ("pro", "专业版 ¥79.2/季度"), ("lifetime", "终身版 ¥399")],
                    format_func=lambda x: x[1],
                    index=1
                )
            with col_n2:
                password = st.text_input("访问密码 *", placeholder="随机生成或自定义", value="")
                if not password:
                    import random
                    import string
                    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                duration_days = st.number_input(
                    "有效天数",
                    min_value=1,
                    max_value=3650,
                    value=90 if plan_type[0] != 'lifetime' else 3650,
                    help="终身版自动设为永久有效"
                )

            notes = st.text_area("备注", placeholder="可选备注信息")

            submitted = st.form_submit_button("✅ 添加用户", use_container_width=True, type="primary")
            if submitted:
                if not wechat:
                    st.error("请填写微信昵称")
                else:
                    actual_plan = plan_type[0]
                    try:
                        user_id = add_user(wechat, password, actual_plan, duration_days)
                        st.success(f"✅ 用户添加成功！")
                        st.info(f"""
                        - **微信昵称**: {wechat}
                        - **套餐**: {plan_type[1]}
                        - **访问密码**: `{password}`
                        - **有效期限**: {'永久' if actual_plan == 'lifetime' else f'{duration_days} 天'}
                        """)
                    except Exception as e:
                        st.error(f"添加失败：{str(e)}")

    with tab_list:
        st.markdown("### 用户列表")
        users = list_all_users()
        if users:
            user_data = []
            for u in users:
                expire = u.get('expire_date', '')
                if isinstance(expire, str) and expire == '9999-12-31':
                    expire_display = "永久"
                else:
                    expire_display = str(expire) if expire else "未知"

                plan_names = {'basic': '基础版', 'pro': '专业版', 'lifetime': '终身版'}
                user_data.append({
                    'ID': u.get('user_id'),
                    '微信昵称': u.get('wechat_nickname', ''),
                    '套餐': plan_names.get(u.get('plan_type', ''), u.get('plan_type', '')),
                    '开始日期': str(u.get('start_date', '')),
                    '到期日期': expire_display,
                    '状态': '✅ 有效' if u.get('is_active') else '❌ 已禁用',
                    '创建时间': str(u.get('created_at', ''))[:10],
                })
            df_users = pd.DataFrame(user_data)
            st.dataframe(df_users, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("### 管理操作")
            col_m1, col_m2, col_m3 = st.columns(3)

            with col_m1:
                st.markdown("**续费用户**")
                renew_id = st.number_input("用户ID", min_value=1, key="renew_id")
                renew_days = st.number_input("续费天数", min_value=1, value=90, key="renew_days")
                if st.button("续费", use_container_width=True):
                    try:
                        extend_user_expiry(renew_id, renew_days)
                        st.success(f"用户 {renew_id} 已续费 {renew_days} 天")
                        st.rerun()
                    except Exception as e:
                        st.error(f"续费失败：{str(e)}")

            with col_m2:
                st.markdown("**禁用/启用用户**")
                toggle_id = st.number_input("用户ID", min_value=1, key="toggle_id")
                toggle_status = st.selectbox("操作", ["禁用", "启用"])
                if st.button("执行", use_container_width=True):
                    try:
                        toggle_user_active(toggle_id, toggle_status == "启用")
                        st.success(f"用户 {toggle_id} 已{'启用' if toggle_status == '启用' else '禁用'}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"操作失败：{str(e)}")

            with col_m3:
                st.markdown("**清除过期数据**")
                grace_days = st.number_input("宽限天数", min_value=0, value=30, key="grace_days")
                if st.button("清除过期用户数据", use_container_width=True, type="secondary"):
                    try:
                        delete_expired_user_data(grace_days)
                        st.success(f"已清除 {grace_days} 天前的过期用户数据")
                    except Exception as e:
                        st.error(f"清除失败：{str(e)}")
        else:
            st.info("暂无用户数据")

    with tab_maintain:
        st.markdown("### 系统维护")

        if st.button("🔄 清除过期用户", use_container_width=True):
            from db import cleanup_expired_users
            cleanup_expired_users()
            st.success("已清理过期用户")

        st.markdown("---")
        st.markdown("### 数据导出")
        export_format = st.selectbox("导出格式", ["Excel (.xlsx)", "CSV (.csv)"])
        if st.button("📥 导出所有用户数据", use_container_width=True):
            current_user_id = get_user_id()
            if current_user_id:
                data = export_user_data(current_user_id)
                if data:
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for sheet_name, df in data.items():
                            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                    st.download_button(
                        label="下载 Excel 文件",
                        data=output.getvalue(),
                        file_name=f"temu_user_data_{date.today().isoformat()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("暂无数据可导出")

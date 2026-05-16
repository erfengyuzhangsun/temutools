import streamlit as st
from datetime import datetime, date
from typing import Optional, Dict
from db import verify_user_password, cleanup_expired_users
from common.rate_limiter import (
    check_login_rate_limit, record_login_attempt,
    clear_login_attempts, LoginRateLimitResult, get_client_ip,
)


SESSION_KEY = "auth_user"
SESSION_EXPIRE_DAYS = 7


def is_authenticated() -> bool:
    return SESSION_KEY in st.session_state and st.session_state[SESSION_KEY] is not None


def get_current_user() -> Optional[Dict]:
    if not is_authenticated():
        return None
    user = st.session_state[SESSION_KEY]
    if 'login_time' in user:
        login_time = user['login_time']
        if isinstance(login_time, str):
            login_time = datetime.strptime(login_time, "%Y-%m-%d %H:%M:%S")
        days_elapsed = (datetime.now() - login_time).days
        if days_elapsed >= SESSION_EXPIRE_DAYS:
            logout()
            return None
    return user


def login(password: str) -> Dict:
    cleanup_expired_users()
    client_ip = get_client_ip()
    rate_result = check_login_rate_limit(client_ip)
    if rate_result == LoginRateLimitResult.BLOCKED:
        return {"success": False, "message": "登录尝试过于频繁，请30分钟后再试"}
    user = verify_user_password(password)
    if user is None:
        record_login_attempt(client_ip, password)
        return {"success": False, "message": "密码错误，请联系客服获取正确的访问密码"}
    if isinstance(user, dict) and user.get("error") == "expired":
        record_login_attempt(client_ip, password)
        return {"success": False, "message": "您的套餐已过期，请联系客服续费"}
    clear_login_attempts(client_ip)
    user['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state[SESSION_KEY] = user
    return {"success": True, "user": user}


def logout():
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]


def get_user_plan_type() -> str:
    user = get_current_user()
    return user.get('plan_type', 'basic') if user else 'basic'


def get_user_id() -> Optional[int]:
    user = get_current_user()
    return user.get('user_id') if user else None


def get_user_info() -> Dict:
    user = get_current_user()
    if not user:
        return {}
    return {
        'user_id': user.get('user_id'),
        'wechat_nickname': user.get('wechat_nickname', ''),
        'plan_type': user.get('plan_type', 'basic'),
        'expire_date': user.get('expire_date', ''),
        'start_date': user.get('start_date', ''),
    }


def show_login_page():
    from landing import show_landing_page

    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 60px auto;
            padding: 2.5rem;
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
        }
        .login-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-container">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</div>
        <div class="login-title">跨境卖家运营辅助工具</div>
        <div class="login-subtitle">请输入访问密码，开启您的运营管理之旅</div>
    </div>
    """, unsafe_allow_html=True)

    password = st.text_input("访问密码", type="password", placeholder="请输入您的访问密码", label_visibility="collapsed")

    with st.expander("📋 查看隐私政策与用户协议", expanded=False):
        from privacy_policy import get_privacy_policy_html
        st.markdown(get_privacy_policy_html(), unsafe_allow_html=True)

    privacy_consent = st.checkbox(
        "我已阅读并同意《隐私政策》，了解我的数据将加密存储、仅用于功能服务，不会泄露给任何第三方",
        value=False,
        help="您需要同意隐私政策后才能使用本工具",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔑 验证身份", use_container_width=True, type="primary"):
            if not password:
                st.error("请输入访问密码")
            elif not privacy_consent:
                st.error("请先阅读并同意《隐私政策》")
            else:
                result = login(password)
                if result["success"]:
                    st.success("验证通过！正在跳转...")
                    st.rerun()
                else:
                    st.error(result["message"])

    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <p style="color: #999; font-size: 0.85rem;">
            还没有访问密码？请联系微信：<strong>returnHuangMuNing</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    try:
        show_landing_page()
    except Exception:
        st.info("💡 页面加载中，请稍候...")

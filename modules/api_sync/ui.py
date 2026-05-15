import streamlit as st
import pandas as pd
from datetime import datetime
from modules.api_sync.service import ApiSyncService
from common.async_runner import run as run_async
from modules.api_sync.schemas import SyncStatus


def show_page():
    st.markdown('<p class="main-header">🔄 API对接与数据同步</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">多店铺订单同步 · 增量去重 · 同步历史追溯</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2, tab3 = st.tabs(["📥 数据同步", "🏪 店铺管理", "📜 同步历史"])

    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### 选择同步店铺")
            shops = _get_user_shops(user_id)
            if shops:
                shop_options = {s["shop_name"]: s["shop_id"] for s in shops}
                selected_shop_name = st.selectbox("店铺", list(shop_options.keys()))
                selected_shop_id = shop_options[selected_shop_name]

                col_sync_type, col_page_size = st.columns(2)
                with col_sync_type:
                    sync_type = st.selectbox("同步类型", ["订单同步", "库存同步", "核价同步", "结算同步"])
                with col_page_size:
                    page_size = st.number_input("每页数量", min_value=10, max_value=200, value=50, step=10)

                if st.button("🚀 开始同步", type="primary", use_container_width=True):
                    type_map = {
                        "订单同步": "order", "库存同步": "inventory",
                        "核价同步": "pricing", "结算同步": "settlement",
                    }
                    from modules.api_sync.schemas import SyncType
                    sync_type_enum = SyncType(type_map[sync_type])

                    with st.spinner(f"正在同步 {selected_shop_name} 的数据..."):
                        service = ApiSyncService(user_id)
                        result = run_async(
                            service.sync_orders(shop_id=selected_shop_id, page_size=page_size, sync_type=sync_type_enum)
                        )

                    if result.success:
                        data = result.data or {}
                        st.success(f"✅ {result.message}")
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        col_m1.metric("新增订单", data.get("synced_count", 0))
                        col_m2.metric("去重跳过", data.get("duplicate_skipped", 0))
                        col_m3.metric("API总数", data.get("total_in_api", 0))
                        col_m4.metric("耗时", f"{result.duration_seconds:.1f}s")

                        if data.get("warnings"):
                            with st.expander("⚠️ 数据质量警告"):
                                for w in data["warnings"]:
                                    st.warning(w)
                    else:
                        st.error(f"❌ 同步失败: {result.message}")
                        if result.error_code:
                            st.code(f"错误代码: {result.error_code}")
            else:
                st.info("暂无店铺数据，请先在「店铺管理」中绑定店铺")

        with col2:
            st.markdown("#### 📊 同步概览")
            st.markdown("""
            <div class="metric-card">
                <h6>今日同步</h6>
                <p style="font-size: 1.5rem; font-weight: bold;">-</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="metric-card">
                <h6>同步成功率</h6>
                <p style="font-size: 1.5rem; font-weight: bold;">-</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="metric-card">
                <h6>上次同步</h6>
                <p style="font-size: 1.5rem; font-weight: bold;">-</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("""
            <div style="background: #e7f3ff; padding: 1rem; border-radius: 10px;">
                <h6>💡 同步说明</h6>
                <small>
                • 系统自动去重，不会重复导入<br>
                • 建议每日同步1-2次<br>
                • 大批量同步请选择非高峰时段
                </small>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### 绑定新店铺")
        st.caption("新版使用 access_token 授权（推荐）；旧版兼容 API Key + API Secret")

        bind_mode = st.radio("绑定方式", ["🔑 access_token（新版）", "🔐 API Key + Secret（旧版）"],
                             horizontal=True, label_visibility="collapsed")

        with st.form("bind_shop_form"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                shop_name = st.text_input("店铺名称", placeholder="例如：旗舰店-1")
                if bind_mode.startswith("🔑"):
                    access_token = st.text_input("Access Token", type="password",
                        help="卖家授权后获取的 access_token")
                    api_key = ""
                    api_secret = ""
                else:
                    api_key = st.text_input("API Key", type="password")
                    access_token = ""
            with col_f2:
                main_category = st.selectbox("主营类目", [
                    "家居百货", "3C数码", "服装鞋包", "美妆个护",
                    "玩具母婴", "食品饮料", "运动户外", "其他"
                ])
                if not bind_mode.startswith("🔑"):
                    api_secret = st.text_input("API Secret", type="password")
                else:
                    api_secret = ""

            submitted = st.form_submit_button("🔗 绑定店铺", type="primary", use_container_width=True)

            if submitted:
                if not shop_name:
                    st.error("请填写店铺名称")
                elif bind_mode.startswith("🔑") and not access_token:
                    st.error("请填写 Access Token")
                elif not bind_mode.startswith("🔑") and (not api_key or not api_secret):
                    st.error("请填写完整的 API Key 和 API Secret")
                else:
                    from modules.api_sync.schemas import ShopBindRequest
                    request = ShopBindRequest(
                        shop_name=shop_name, api_key=api_key,
                        api_secret=api_secret, access_token=access_token,
                        main_category=main_category,
                    )
                    service = ApiSyncService(user_id)
                    result = run_async(service.bind_shop(request))

                    if result.success:
                        st.success(f"✅ 店铺 {shop_name} 绑定成功")
                    else:
                        st.error(f"❌ 绑定失败: {result.message}")

        st.markdown("---")
        st.markdown("#### 已绑定店铺")
        shops = _get_user_shops(user_id)
        if shops:
            for shop in shops:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{shop['shop_name']}</h4>
                        <p>类目: {shop.get('main_category', '未设置')} | 店铺ID: {shop['shop_id']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("暂无已绑定店铺")

    with tab3:
        st.markdown("#### 同步历史记录")

        shops = _get_user_shops(user_id)
        if shops:
            shop_options = {s["shop_name"]: s["shop_id"] for s in shops}
            selected_shop = st.selectbox("选择店铺查看历史", list(shop_options.keys()))

            if st.button("📋 查询同步历史"):
                service = ApiSyncService(user_id)
                history = run_async(
                    service.get_sync_history(shop_id=shop_options[selected_shop], limit=20)
                )

                if history:
                    records = []
                    for h in history:
                        status_emoji = {
                            SyncStatus.SUCCESS: "✅", SyncStatus.FAILED: "❌",
                            SyncStatus.RUNNING: "🔄", SyncStatus.PENDING: "⏳",
                        }.get(h.status, "❓")
                        records.append({
                            "状态": f"{status_emoji} {h.status.value}",
                            "类型": h.sync_type,
                            "新增": h.synced_count,
                            "耗时": f"{h.duration_seconds:.1f}s",
                            "时间": h.started_at.strftime("%Y-%m-%d %H:%M:%S") if h.started_at else "-",
                            "错误": h.error_message or "-",
                        })
                    st.dataframe(pd.DataFrame(records), width='stretch')
                else:
                    st.info("暂无同步记录")
        else:
            st.info("请先绑定店铺")

    st.markdown("---")
    st.caption("Temu API对接与数据同步模块 | 数据加密传输，安全可靠")


def _get_user_shops(user_id: int) -> list:
    from db import execute_query
    return execute_query(
        "SELECT shop_id, shop_name, main_category FROM temu_shops WHERE user_id = ?",
        (user_id,), fetch=True,
    ) or []

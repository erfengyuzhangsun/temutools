import streamlit as st
from common.api_client_factory import is_mock_mode
from modules.api_sync.service import ApiSyncService
from common.async_runner import run as run_async


def show_page():
    st.markdown('<p class="main-header">🔑 API密钥管理</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">零基础密钥申请指南 · 极简录入 · 连通性自检</p>', unsafe_allow_html=True)

    user_id = st.session_state.get("user_id", 1)

    tab1, tab2 = st.tabs(["🔑 密钥录入", "📖 申请教程"])

    with tab1:
        _render_key_entry(user_id)

    with tab2:
        _render_tutorial()

    st.markdown("---")
    st.caption("API密钥管理 | 仅需填入3个值，系统自动完成加密存储")


def _render_key_entry(user_id: int):
    st.markdown("#### 填入 API 密钥")
    st.caption("所有密钥将使用 Fernet 加密后存入数据库，不会明文存储")

    from db import execute_query
    shops = execute_query(
        "SELECT shop_id, shop_name FROM temu_shops WHERE user_id=?",
        (user_id,), fetch=True,
    ) or []

    shop_options = {s["shop_name"]: s["shop_id"] for s in shops} if shops else {"默认店铺": 0}
    selected_shop = st.selectbox("选择店铺", list(shop_options.keys()))
    shop_id = shop_options[selected_shop]

    existing = None
    if shop_id:
        rows = execute_query(
            "SELECT * FROM temu_shop_credentials WHERE shop_id=?",
            (shop_id,), fetch=True,
        )
        if rows:
            from common.crypto import CryptoUtils
            crypto = CryptoUtils()
            try:
                existing = {
                    "api_key": crypto.decrypt(rows[0]["encrypted_api_key"]),
                    "api_secret": crypto.decrypt(rows[0]["encrypted_api_secret"]),
                    "access_token": crypto.decrypt(rows[0]["encrypted_access_token"]) if rows[0].get("encrypted_access_token") else "",
                }
            except Exception:
                pass

    with st.form("api_key_form"):
        col1, col2 = st.columns(2)
        with col1:
            app_key = st.text_input(
                "App Key *",
                value=existing["api_key"] if existing else "",
                placeholder="点击「申请教程」查看获取位置",
                help="Temu开放平台 → 自研应用管理 → 应用详情",
            )
            app_secret = st.text_input(
                "App Secret *",
                value=existing["api_secret"] if existing else "",
                placeholder="与App Key在同一页面",
                type="password",
                help="应用详情页的 App Secret，请保密",
            )
        with col2:
            access_token = st.text_input(
                "Access Token",
                value=existing["access_token"] if existing else "",
                placeholder="可选，未授权时可留空",
                help="卖家中心 → 授权管理 → 主账号授权后获取",
            )
            st.markdown("##### ")
            st.markdown("##### ")
            submitted = st.form_submit_button("💾 保存密钥", type="primary", use_container_width=True)

    if submitted:
        if not app_key or not app_secret:
            st.error("App Key 和 App Secret 为必填项")
        else:
            service = ApiSyncService(user_id)
            from modules.api_sync.schemas import ShopBindRequest
            request = ShopBindRequest(
                shop_id=shop_id,
                shop_name=selected_shop,
                api_key=app_key,
                api_secret=app_secret,
                access_token=access_token,
            )
            result = run_async(service.bind_shop(request))
            if result.get("success"):
                st.success("✅ 密钥保存成功！")
                st.info("🔍 点击「测试连通性」验证API是否正常工作")
            else:
                st.error(f"❌ 保存失败: {result.get('error', '未知错误')}")

    st.markdown("---")
    if st.button("🔍 测试API连通性", type="primary", use_container_width=True):
        if shop_id <= 0:
            st.error("请先选择有效店铺")
        else:
            result = run_async(_test_connection(shop_id))
            if result["success"]:
                st.success(f"✅ API连接正常！耗时: {result['elapsed']}ms")
                mock_msg = "（当前为模拟模式，数据并非真实API返回）" if is_mock_mode() else ""
                st.info(f"返回数据预览: {result.get('preview', '')} {mock_msg}")
            else:
                st.error(f"❌ 连接失败: {result.get('error', '')}")
                st.info("💡 提示：请检查 App Key / App Secret / Access Token 是否正确")


async def _test_connection(shop_id: int) -> dict:
    import time
    from common.api_client_factory import get_api_client
    start = time.time()
    try:
        client = get_api_client(shop_id)
        resp = await client.check_access_token()
        elapsed = round((time.time() - start) * 1000)
        if resp.success:
            return {"success": True, "elapsed": elapsed, "preview": str(resp.data)[:200]}
        return {"success": False, "error": resp.error or "API响应异常"}
    except Exception as e:
        elapsed = round((time.time() - start) * 1000)
        return {"success": False, "error": str(e), "elapsed": elapsed}


def _render_tutorial():
    st.markdown("#### 📖 API密钥申请图文教程")
    st.info("本教程指引你在 Temu 卖家中心完成 API 密钥申请")

    steps = [
        {
            "step": 1,
            "title": "进入卖家中心 → 服务市场",
            "detail": """
登录 [Temu 卖家中心](https://seller.kuajingmaihuo.com) → 左侧菜单点击「服务市场」→ 选择「自研应用管理」

> 如果找不到「服务市场」，联系你的Temu专属买手申请开通开放平台权限
            """,
        },
        {
            "step": 2,
            "title": "创建自研应用",
            "detail": """
点击「创建新应用」→ 选择「自研应用」类型 → 填写：
- **应用名称**：建议英文名，如 `Cross-border Operations Assistant`
- **应用描述**：说明用途（如"店铺自动化运营管理"）
- **回调地址**：如有网站可填，没有可不填

填写完毕后提交审核，通常 1-3 个工作日通过
            """,
        },
        {
            "step": 3,
            "title": "获取 App Key & App Secret",
            "detail": """
审核通过后 → 点击应用进入详情页 → 即可看到：
- **App Key**（应用标识）
- **App Secret**（应用密钥，请保密，不要泄露）

> 将这两个值填入左侧「密钥录入」页签
            """,
        },
        {
            "step": 4,
            "title": "主账号授权获取 Access Token",
            "detail": """
卖家中心 → 服务市场 → 授权管理
→ 找到你的应用 → 点击「主账号授权」→ 确认授权
→ 授权成功后即可获得 **Access Token**（有效期3个月，到期需重新授权）

> 将 Access Token 填入左侧「密钥录入」页签
            """,
        },
        {
            "step": 5,
            "title": "配置服务器IP白名单",
            "detail": """
应用详情页 → 「IP白名单」设置
→ 添加你的服务器公网IP地址

> 如果不设置IP白名单，API调用会被拒绝
            """,
        },
        {
            "step": 6,
            "title": "验证连通性",
            "detail": """
填入三个密钥后 → 点击「测试连通性」按钮
→ 如果显示"API连接正常"，说明配置成功！
→ 如果连接失败，请检查：
  1. App Key / App Secret 是否正确
  2. Access Token 是否已授权且未过期
  3. 服务器IP是否在白名单内
            """,
        },
    ]

    for s in steps:
        with st.expander(f"**Step {s['step']}**: {s['title']}", expanded=False):
            st.markdown(s["detail"])

    st.markdown("---")
    st.markdown("#### ❓ 常见问题")

    faqs = [
        ("申请API权限需要什么条件？", "通常需要店铺有100件以上在售商品，或联系买手申请开通"),
        ("Access Token 有效期多长？", "3个月，到期后需要在授权管理中重新授权"),
        ("App Secret 忘了怎么办？", "在应用详情页可以重置 App Secret，重置后原Secret立即失效"),
        ("API调用量有限制吗？", "Temu API 有频率限制，建议合理控制调用频率，避免被封"),
    ]
    for q, a in faqs:
        with st.expander(q, expanded=False):
            st.markdown(a)

import streamlit as st
from modules.server_monitor.notifications import NotificationManager

def render_notification_config():
    st.header("🔔 告警通知配置")
    st.caption("配置 Webhook 通知渠道，支持钉钉、企业微信、飞书等平台")

    manager = NotificationManager()
    platform_info = manager.get_platform_info()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📱 支持的平台")
        for platform, info in platform_info.items():
            status_emoji = "✅" if info["configured"] and info["enabled"] else "⚪"
            status_text = "已启用" if info["configured"] and info["enabled"] else ("已配置未启用" if info["configured"] else "未配置")
            st.markdown(f"{status_emoji} **{info['name']}** - {status_text}")

    with col2:
        st.subheader("⚙️ 快速配置")
        selected_platform = st.selectbox(
            "选择平台",
            options=list(platform_info.keys()),
            format_func=lambda x: platform_info[x]["name"]
        )

        if selected_platform:
            config_help = {
                "dingtalk": """
                **钉钉机器人配置步骤：**
                1. 打开钉钉群 → 设置 → 智能群助手
                2. 添加机器人 → 自定义 → 通过Webhook接入
                3. 复制 Webhook 地址和加签密钥（可选）
                """,
                "wechat_work": """
                **企业微信配置步骤：**
                1. 打开企业微信群 → 右上角 + → 添加群机器人
                2. 设置机器人名称和头像
                3. 复制 Webhook 地址
                """,
                "feishu": """
                **飞书机器人配置步骤：**
                1. 打开飞书群 → 设置 → 群机器人
                2. 添加机器人 → 自定义机器人
                3. 复制 Webhook 地址
                """,
                "generic": """
                **通用 Webhook 配置：**
                1. 准备一个可接收 HTTP POST 请求的 URL
                2. 确保 URL 可从公网访问
                3. 请求体格式为 JSON
                """
            }
            
            st.markdown(config_help.get(selected_platform, ""))

    st.markdown("---")

    webhook_url = st.text_input(
        "🔗 Webhook URL",
        value="",
        type="password",
        help=f"输入 {platform_info[selected_platform]['name']} 的 Webhook 地址"
    )

    webhook_secret = st.text_input(
        "🔐 加密密钥 (可选)",
        value="",
        type="password",
        help="钉钉机器人的加签密钥，其他平台可留空"
    )

    col_save, col_test = st.columns(2)

    with col_save:
        if st.button("💾 保存配置", type="primary", disabled=not webhook_url):
            try:
                manager.add_webhook(selected_platform, webhook_url, webhook_secret or None)
                
                env_mapping = {
                    "dingtalk": "DINGTALK_WEBHOOK_URL",
                    "wechat_work": "WECHAT_WORK_WEBHOOK_URL",
                    "feishu": "FEISHU_WEBHOOK_URL",
                    "generic": "GENERIC_WEBHOOK_URL"
                }
                
                st.success(f"✅ {platform_info[selected_platform]['name']} 配置已保存！")
                st.info(f"💡 请将以下环境变量添加到 `.env` 文件：\n\n```\n{env_mapping[selected_platform]}={webhook_url}\n```")
                
                if webhook_secret:
                    secret_mapping = {
                        "dingtalk": "DINGTALK_WEBHOOK_SECRET"
                    }
                    if selected_platform in secret_mapping:
                        st.info(f"```\n{secret_mapping[selected_platform]}={webhook_secret}\n```")
                        
            except Exception as e:
                st.error(f"❌ 保存失败: {str(e)}")

    with col_test:
        if st.button("🧪 发送测试消息", disabled=not webhook_url):
            with st.spinner("正在发送测试消息..."):
                import asyncio
                
                test_alert = {
                    "type": "test",
                    "level": "info",
                    "message": "这是一条来自 Temu 运营平台的测试告警消息",
                    "metric_value": 0,
                    "threshold": 0,
                    "timestamp": "测试时间"
                }
                
                try:
                    manager.add_webhook(selected_platform, webhook_url, webhook_secret or None)
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(manager.send_alert(test_alert))
                        finally:
                            loop.close()
                    
                    for platform, response in result.items():
                        if response.get("success"):
                            st.success(f"✅ {response['message']}")
                        else:
                            st.error(f"❌ {response.get('message', '发送失败')}")
                            
                except Exception as e:
                    st.error(f"❌ 测试失败: {str(e)}")

    st.markdown("---")
    
    with st.expander("📖 详细说明", expanded=False):
        st.markdown("""
        ### 🔔 告警通知工作原理
        
        1. **监控检测**：系统定期检查 CPU、内存、磁盘等指标
        2. **阈值判断**：当指标超过设定阈值时触发告警
        3. **去重处理**：相同类型的告警在冷却期内不会重复发送
        4. **格式转换**：将告警信息转换为各平台支持的格式
        5. **发送通知**：通过 Webhook 发送到配置的聊天平台
        
        ### 🎯 告警级别说明
        
        | 级别 | 图标 | 含义 | 处理建议 |
        |------|------|------|----------|
        | critical | 🔴 | 严重 | 立即处理，可能影响服务可用性 |
        | warning | 🟡 | 警告 | 尽快处理，可能在未来恶化 |
        | info | 🔵 | 信息 | 一般通知，供参考 |
        
        ### ⏰ 冷却机制
        
        为避免告警轰炸，系统采用智能冷却机制：
        - 默认冷却时间：**5 分钟**
        - 相同类型和级别的告警在冷却期内只发送一次
        - 不同级别的告警会立即发送
        - 可在 `modules/server_monitor/config.py` 中调整 `alert_cooldown_seconds`
        
        ### 🔒 安全建议
        
        - Webhook URL 包含敏感信息，请妥善保管
        - 建议使用带权限验证的机器人
        - 定期轮换 Webhook Token
        - 生产环境建议使用 HTTPS 协议
        """)

import streamlit as st
from datetime import datetime
from db import save_landing_order, initialize_database

PLAN_PRICES = {
    "基础版 - ¥39.9/月": 39.9,
    "专业版 - ¥79.2/季度（推荐）": 79.2,
    "终身版 - ¥399": 399.0,
}

def show_landing_page():
    if 'db_initialized' not in st.session_state:
        try:
            initialize_database()
            st.session_state['db_initialized'] = True
        except Exception:
            pass
    try:
        st.set_page_config(
            page_title="Temu全托管自动化运营平台 - 告别熬夜盯后台",
            page_icon="🤖",
            layout="wide"
        )
    except Exception:
        pass

    try:
        query_params = st.query_params
        selected_plan = query_params.get("plan", [""])[0] if "plan" in query_params else ""
    except Exception as e:
        selected_plan = ""

    if 'order_submitted' not in st.session_state:
        st.session_state['order_submitted'] = False
    if 'order_info' not in st.session_state:
        st.session_state['order_info'] = {}

    st.markdown("""
    <style>
        /* ========== 全局样式 ========== */
        * { box-sizing: border-box; }

        /* ========== Hero 区域（超紧凑版） ========== */
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 1.2rem;
            border-radius: 14px;
            text-align: center;
            margin-bottom: 1.2rem;
            position: relative;
            overflow: hidden;
        }

        .hero-title { font-size: 2.4rem; font-weight: bold; margin-bottom: 0.6rem; position: relative; z-index: 1; }
        .hero-subtitle { font-size: 1.1rem; opacity: 0.95; margin-bottom: 1rem; position: relative; z-index: 1; line-height: 1.5; }

        /* ========== 紧急通知横幅（超紧凑） ========== */
        .urgency-banner {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 0.8rem 1.2rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(255, 107, 107, 0.25);
        }

        /* ========== 社会证明数据条（超紧凑） ========== */
        .social-proof-bar {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }

        .stat-item { text-align: center; padding: 0.5rem; }
        .stat-number { font-size: 1.7rem; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .stat-label { color: #666; font-size: 0.85rem; margin-top: 0.2rem; }

        /* ========== 功能卡片（超紧凑） ========== */
        .feature-card {
            background: white;
            padding: 1.1rem;
            border-radius: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            height: 100%;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }

        .feature-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.18); border-color: #667eea; }

        /* ========== 解决方案卡片（三段式） ========== */
        .solution-card {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.07);
            height: 100%;
            transition: all 0.3s ease;
            border-top: 4px solid #667eea;
        }
        .solution-card:hover { transform: translateY(-4px); box-shadow: 0 6px 18px rgba(102, 126, 234, 0.18); }
        .solution-tag {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.15rem 0.6rem;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-bottom: 0.4rem;
        }
        .solution-result {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            padding: 0.5rem 0.7rem;
            border-radius: 8px;
            margin-top: 0.5rem;
            font-size: 0.85rem;
            font-weight: bold;
            color: #155724;
        }

        /* ========== 价值标签 ========== */
        .value-tag {
            display: inline-block;
            background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
            color: white;
            padding: 0.2rem 0.7rem;
            border-radius: 12px;
            font-size: 0.78rem;
            font-weight: bold;
            margin-top: 0.4rem;
        }

        /* ========== 定价卡片（超紧凑） ========== */
        .pricing-card {
            background: white;
            padding: 1.5rem 1.1rem;
            border-radius: 14px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
            border: 2px solid transparent;
        }

        .pricing-card:hover { transform: translateY(-6px) scale(1.02); box-shadow: 0 10px 28px rgba(0,0,0,0.15); }

        .pricing-card.popular {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            transform: scale(1.03);
            border: 2px solid #ffd700;
            box-shadow: 0 10px 28px rgba(102, 126, 234, 0.35);
        }

        .pricing-card.popular::before {
            content: '⭐ 最受欢迎 · 90%卖家首选';
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #333;
            padding: 0.25rem 1.2rem;
            border-radius: 16px;
            font-weight: bold;
            font-size: 0.85rem;
            box-shadow: 0 3px 10px rgba(255, 215, 0, 0.35);
        }

        .price-amount { font-size: 2.3rem; font-weight: bold; margin: 0.6rem 0; }
        .price-savings { display: inline-block; background: #28a745; color: white; padding: 0.15rem 0.5rem; border-radius: 8px; font-size: 0.75rem; margin-left: 0.3rem; }

        /* ========== CTA 按钮（超紧凑） ========== */
        .cta-button-primary {
            background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%) !important;
            color: white !important;
            padding: 0.75rem 2rem !important;
            border-radius: 35px !important;
            font-size: 1rem !important;
            font-weight: bold !important;
            border: none !important;
            cursor: pointer !important;
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.35) !important;
            display: inline-block !important;
            margin: 0.6rem 0 !important;
            text-decoration: none !important;
            transition: all 0.3s ease !important;
        }

        .cta-button-primary:hover { transform: scale(1.06) !important; box-shadow: 0 8px 24px rgba(255, 107, 53, 0.5) !important; }

        .cta-button-secondary {
            background: #6c757d !important;
            color: white !important;
            padding: 0.65rem 1.7rem !important;
            border-radius: 35px !important;
            font-size: 0.92rem !important;
            font-weight: bold !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            display: inline-block !important;
            margin: 0.5rem 0 !important;
            text-decoration: none !important;
        }

        .cta-button-secondary:hover { background: #5a6268 !important; transform: scale(1.04); }

        /* ========== CTA 透明边框按钮 ========== */
        .cta-button-outline {
            background: transparent !important;
            color: white !important;
            padding: 0.65rem 1.7rem !important;
            border-radius: 35px !important;
            font-size: 0.92rem !important;
            font-weight: bold !important;
            border: 2px solid rgba(255,255,255,0.7) !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            display: inline-block !important;
            margin: 0.5rem 0 !important;
            text-decoration: none !important;
        }
        .cta-button-outline:hover { background: rgba(255,255,255,0.15) !important; border-color: white !important; transform: scale(1.04); }

        /* ========== 收款码区域（超紧凑） ========== */
        .payment-section {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1.5rem 1.2rem;
            border-radius: 16px;
            margin-top: 1.5rem;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            border: 2px dashed #dee2e6;
        }

        .qr-code-container {
            text-align: center;
            padding: 0.8rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.07);
            transition: all 0.3s ease;
        }

        .qr-code-container:hover { transform: scale(1.02); box-shadow: 0 6px 18px rgba(0,0,0,0.12); }
        .qr-label { font-weight: bold; font-size: 0.95rem; margin-bottom: 0.5rem; display: block; }

        /* ========== 退款保证徽章（超紧凑） ========== */
        .guarantee-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 0.5rem 1.2rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.88rem;
            box-shadow: 0 3px 12px rgba(40, 167, 69, 0.25);
            margin: 0.8rem 0;
        }

        /* ========== 用户评价卡片（超紧凑） ========== */
        .testimonial-card {
            background: white;
            padding: 1.1rem;
            border-radius: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.07);
            margin: 0.6rem 0;
            border-left: 4px solid #ffc107;
            transition: all 0.3s ease;
        }

        .testimonial-card:hover { transform: translateX(6px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); }

        /* ========== 痛点卡片（反问句风格） ========== */
        .pain-point {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
            padding: 0.75rem;
            border-left: 4px solid #ffc107;
            border-radius: 8px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 6px rgba(255, 193, 7, 0.12);
            transition: all 0.3s ease;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .pain-point:hover { transform: translateX(-4px); box-shadow: 0 3px 10px rgba(255, 193, 7, 0.2); }

        .solution-point {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            padding: 0.75rem;
            border-left: 4px solid #28a745;
            border-radius: 8px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 6px rgba(40, 167, 69, 0.12);
            transition: all 0.3s ease;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .solution-point:hover { transform: translateX(4px); box-shadow: 0 3px 10px rgba(40, 167, 69, 0.2); }

        /* ========== FAQ 区域（超紧凑 + 完全修复HTML） ========== */
        .faq-section {
            background: #f8f9fa;
            padding: 1.1rem;
            border-radius: 12px;
            margin: 0.6rem 0;
        }

        .faq-item {
            margin: 0.6rem 0;
            padding: 0.7rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }

        .faq-question {
            color: #333;
            font-weight: bold;
            font-size: 0.92rem;
            margin-bottom: 0.3rem;
        }

        .faq-answer {
            color: #555;
            font-size: 0.87rem;
            line-height: 1.5;
        }

        /* ========== 联系方式卡片（超紧凑） ========== */
        .contact-card {
            background: white;
            padding: 0.85rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        }

        .contact-title {
            font-size: 0.92rem;
            color: #333;
            font-weight: bold;
            margin-bottom: 0.3rem;
        }

        .contact-value {
            font-size: 0.98rem;
            font-weight: bold;
            color: #667eea;
        }

        .contact-note {
            font-size: 0.8rem;
            color: #888;
            margin-top: 0.2rem;
        }

        /* ========== 用户画像标签 ========== */
        .user-tag {
            display: inline-block;
            background: #e9ecef;
            padding: 0.15rem 0.6rem;
            border-radius: 8px;
            font-size: 0.78rem;
            color: #555;
            margin: 0.2rem;
        }

        /* ========== 响应式设计（移动端 - 超紧凑） ========== */
        @media (max-width: 768px) {
            .hero-title { font-size: 1.6rem !important; }
            .hero-subtitle { font-size: 0.95rem !important; }
            .hero-section { padding: 1.5rem 1rem !important; }
            .price-amount { font-size: 1.9rem !important; }
            .stat-number { font-size: 1.4rem !important; }
            .pricing-card { padding: 1.2rem 0.8rem !important; margin-bottom: 0.8rem !important; }
            .pricing-card.popular { transform: scale(1) !important; }
            .cta-button-primary { padding: 0.7rem 1.8rem !important; font-size: 0.92rem !important; width: 100% !important; max-width: 260px; }
            .payment-section { padding: 1.2rem 0.8rem !important; }
            .qr-code-container img { width: 180px !important; height: 180px !important; }
            .feature-card { padding: 0.95rem !important; margin-bottom: 0.6rem !important; }
            .urgency-banner { padding: 0.7rem 1rem !important; font-size: 0.85rem !important; }
            .social-proof-bar { padding: 1rem 0.6rem !important; }
            .testimonial-card { padding: 0.95rem !important; }
            .pain-point, .solution-point { padding: 0.65rem !important; font-size: 0.85rem !important; }
            .solution-card { padding: 0.85rem !important; }
        }

        /* ========== 隐藏 Streamlit 默认元素 ========== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* ========== 滚动条美化 ========== */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 4px; }

        /* ========== 强制亮色主题（覆盖系统深色模式） ========== */
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        .stApp, .main, .block-container {
            background-color: #FFFFFF !important;
            color: #1E1E1E !important;
        }
        html, body, .stApp, .main, .block-container,
        p, h1, h2, h3, h4, h5, h6, span, div, label,
        .stMarkdown, .stText {
            color: #1E1E1E !important;
        }
        .stSidebar, [data-testid="stSidebar"] {
            background-color: #F8F9FA !important;
        }
        .stSidebar * {
            color: #1E1E1E !important;
        }
        input, textarea, select, [data-baseweb="input"] input {
            background-color: #FFFFFF !important;
            color: #1E1E1E !important;
        }
        /* 覆盖深色模式下Streamlit默认文本颜色 */
        .css-1y4p8pa, .css-1r6goiv, .css-1v3fvcr, .css-1x8cf1d,
        .css-1n76uvr, .css-1cpxqw2, .css-1q8ddro {
            color: #1E1E1E !important;
        }
        /* 确保侧边栏导航按钮文字可见 */
        [data-testid="baseButton-secondary"] {
            color: #1E1E1E !important;
        }
    </style>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        if (window.location.hash) {
            setTimeout(function() {
                var el = document.querySelector(window.location.hash);
                if (el) el.scrollIntoView({behavior: 'smooth'});
            }, 200);
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # ==================== 1️⃣ Hero Section ====================
    st.markdown("""
    <div class="hero-section">
        <div style="font-size: 0.85rem; opacity: 0.8; margin-bottom: 0.4rem; position: relative; z-index: 1;">🤖 Temu全托管自动化运营平台</div>
        <div class="hero-title">告别熬夜盯后台<br>Temu运营，交给AI全自动搞定</div>
        <div class="hero-subtitle">
            核价、库存、调价、活动、发货、售后全流程自动化<br>
            <strong>每天仅需5分钟，其余时间躺平</strong>
        </div>
        <div style="margin-top: 1rem; position: relative; z-index: 1; display: flex; gap: 0.8rem; justify-content: center; flex-wrap: wrap;">
            <a href="?page=app" class="cta-button-primary" style="color: white; text-decoration: none;">🚀 免费试用7天，开启躺平运营</a>
            <a href="#solutions" class="cta-button-outline" style="color: white; text-decoration: none;">▶ 查看自动化全流程演示</a>
        </div>
        <div style="margin-top: 1rem; display: flex; gap: 1.2rem; justify-content: center; flex-wrap: wrap; position: relative; z-index: 1; font-size: 0.82rem; opacity: 0.9;">
            <span>✅ 已帮 800+ 卖家实现 90% 运营自动化</span>
            <span>✅ 单店月均节省人工成本 3000+ 元</span>
            <span>✅ 用户满意度 4.9/5，零差评退款</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_enter1, col_enter2, col_enter3 = st.columns([1, 2, 1])
    with col_enter2:
        if st.button("🚪 进入应用", use_container_width=True, type="primary"):
            st.session_state["page"] = "app"
            st.query_params["page"] = "app"

    # ==================== 2️⃣ 紧迫感横幅 ====================
    st.markdown("""
    <div class="urgency-banner">
        <h3 style="margin: 0 0 0.3rem 0; font-size: 1.15rem;">🎉 累计服务800+卖家，首发专属：前 <strong>100</strong> 名新用户享 <strong>8折</strong></h3>
        <p style="margin: 0; font-size: 0.92rem; opacity: 0.95;">
            专业版原价 ¥99/季度，现价 <strong style="font-size: 1.05rem;">¥79.2/季度</strong> |
            仅剩 <strong style="color: #FFE66D; font-size: 1.05rem;">23</strong> 个名额 |
            ⏰ 截止：2026年5月19日
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ==================== 3️⃣ 社会证明数据条 ====================
    st.markdown("<div class='social-proof-bar'>", unsafe_allow_html=True)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    with col_s1:
        st.markdown("""<div class="stat-item"><div class="stat-number">800+</div><div class="stat-label">👥 累计合作卖家</div></div>""", unsafe_allow_html=True)

    with col_s2:
        st.markdown("""<div class="stat-item"><div class="stat-number">90%</div><div class="stat-label">🤖 运营工作已自动化</div></div>""", unsafe_allow_html=True)

    with col_s3:
        st.markdown("""<div class="stat-item"><div class="stat-number">¥3000+</div><div class="stat-label">💰 单店月均节省成本</div></div>""", unsafe_allow_html=True)

    with col_s4:
        st.markdown("""<div class="stat-item"><div class="stat-number">4.9/5</div><div class="stat-label">⭐ 用户满意度 · 零差评退款</div></div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==================== 4️⃣ 痛点模块：6个反问句 ====================
    st.markdown("## 😰 这些Temu运营难题，你中了几个？")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("""
        <div class="pain-point"><strong>❓ 每天手动核价、算利润，算到凌晨还在亏？</strong><br>核价通知一来就紧张，手动算半天还怕算错，月底一结算发现白干</div>
        <div class="pain-point"><strong>❓ 竞品降价手动跟价，反应慢就丢单，还守不住毛利？</strong><br>不跟→没单，跟了→亏本，手动盯价格盯到眼睛疼，还总是慢半拍</div>
        <div class="pain-point"><strong>❓ 库存断货/滞销，一边亏流量一边压资金？</strong><br>爆款断货丢排名，滞销品堆在仓库天天亏仓储费，库存永远管不好</div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown("""
        <div class="pain-point"><strong>❓ 活动报名错过时间，大促活动只能看着别人爆单？</strong><br>活动通知太多看不过来，等想起来报名已经截止，流量全给别人了</div>
        <div class="pain-point"><strong>❓ 售后消息、处罚通知漏看，店铺分一路掉？</strong><br>一天几百条消息，重要通知被淹没，漏看一条处罚就扣分罚款</div>
        <div class="pain-point"><strong>❓ 数据报表要做1小时，还找不到问题在哪？</strong><br>每天花大量时间做表，做完也不知道该优化哪里，问题越积越多</div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==================== 5️⃣ 解决方案模块：8个三段式 ====================
    st.markdown("""<h2 id="solutions">🚀 全流程自动化，每个环节都帮你赚钱</h2>""", unsafe_allow_html=True)

    sol_rows = [
        [
            ("全自动核价", "零漏单、零亏损，再也不用熬夜核价", 
             "手动核价30分钟，还漏处理导致商品下架",
             "按预设毛利规则批量自动处理核价通知，超时强提醒",
             "每天省30分钟，零漏单、零亏损"),
            ("库存智能管理", "防断货、防积压，资金和流量双保住",
             "断货丢流量，滞销压资金",
             "安全库存预警+销量预测+滞销SKU识别，自动生成补货建议",
             "库存周转提升40%，资金占用直降30%"),
        ],
        [
            ("智能自动调价", "跟价不亏，守住每一分利润",
             "跟价就亏，不跟价就没单",
             "竞品实时监控+保本毛利锁定+活动价定时切换",
             "保毛利前提下自动跟价，单店利润提升15%"),
            ("活动自动报名", "一键匹配，再也不亏活动流量",
             "手动找活动、筛选SKU，错过报名时间",
             "自动抓取可报活动+SKU匹配+批量报名+状态追踪",
             "大促活动100%参与，再也不亏活动流量"),
        ],
        [
            ("数据自动分析预警", "自动找问题，每天5分钟掌握店铺状态",
             "做报表1小时，还找不到问题",
             "每日自动生成报表，异常指标实时预警，给出优化建议",
             "1小时人工工作，压缩为5分钟全自动出结果"),
            ("消息与售后自动化", "每天省15分钟，零漏看平台通知",
             "消息太多看不过来，处罚通知漏看",
             "消息智能分类+重要通知强提醒+售后模板一键复用",
             "每天省15分钟，零漏看平台通知"),
        ],
        [
            ("标签与发货自动化", "1小时备货压缩到20分钟",
             "手动生成标签1小时，容易出错",
             "批量生成平台规范标签/箱唛，同步物流信息",
             "1小时备货发货，压缩到20分钟内完成"),
            ("多店铺统一总控", "一个后台管所有店，运营状态一目了然",
             "多店铺来回切换后台，信息混乱",
             "一个后台管理所有店铺，盈亏/待办/告警一站式查看",
             "多店运营效率提升60%，告别多窗口来回切"),
        ],
    ]

    for row in sol_rows:
        cols = st.columns(2)
        for idx, (name, tag, pain, solution, result) in enumerate(row):
            with cols[idx]:
                st.markdown(f"""
                <div class="solution-card">
                    <div class="solution-tag">{tag}</div>
                    <h3 style="margin: 0.3rem 0 0.5rem 0; font-size: 1.05rem; color: #333;">{name}</h3>
                    <div style="font-size: 0.85rem; line-height: 1.6;">
                        <div style="color: #dc3545; margin-bottom: 0.3rem;">😖 <strong>痛点：</strong>{pain}</div>
                        <div style="color: #667eea; margin-bottom: 0.3rem;">🛠 <strong>方案：</strong>{solution}</div>
                    </div>
                    <div class="solution-result">📈 结果：{result}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ==================== 6️⃣ 核心功能展示（带价值标签） ====================
    st.markdown("## 🎯 核心功能")

    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        st.markdown("""
        <div class="feature-card">
            <div class="value-tag">零漏单、零亏损，再也不用熬夜核价</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">📊 全自动核价模块</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 🔄 批量导入订单自动匹配核价规则<br>
                • 🤖 按预设毛利自动接受/拒绝核价通知<br>
                • ⏰ 超时未处理自动强提醒，不漏单<br>
                • � 核价记录全留痕，可追溯可撤销<br>
                • 📉 利润低于阈值自动拦截，防止亏损
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_f2:
        st.markdown("""
        <div class="feature-card">
            <div class="value-tag">防断货、防积压，资金和流量双保住</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">📦 库存智能管理</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 📈 库存销量趋势实时追踪<br>
                • 🚨 安全库存预警，断货前自动提醒<br>
                • 📉 滞销SKU自动识别+清仓建议<br>
                • 🔮 AI销量预测辅助补货决策<br>
                • 📄 自动生成补货建议单
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_f3:
        st.markdown("""
        <div class="feature-card">
            <div class="value-tag">跟价不亏，守住每一分利润</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">📈 智能自动调价</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • � 竞品价格实时监控，变动即时预警<br>
                • � 保本毛利底线锁定，跟价不亏本<br>
                • � 活动价/日常价定时自动切换<br>
                • � 调价历史全记录，利润变化一目了然<br>
                • ⚙ 支持按店铺/SKU维度独立策略
            </p>
        </div>
        """, unsafe_allow_html=True)

    col_f4, col_f5, col_f6 = st.columns(3)

    with col_f4:
        st.markdown("""
        <div class="feature-card">
            <div class="value-tag">一键匹配，再也不亏活动流量</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">🎯 平台活动自动报名</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 🔍 自动抓取可报名活动，智能匹配店铺SKU<br>
                • 📋 一键批量报名，省去逐个筛选时间<br>
                • 📊 活动状态追踪，已报/待报一目了然<br>
                • ⏰ 报名截止前自动提醒，不错过任何大促<br>
                • 📈 活动效果数据复盘
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_f5:
        st.markdown("""
        <div class="feature-card">
            <div class="value-tag">自动找问题，每天5分钟掌握店铺状态</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">� 数据自动分析与预警</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 📋 每日自动生成运营日报，数据不遗漏<br>
                • 🚨 异常指标实时预警（利润/库存/风险等）<br>
                • 💡 AI自动分析问题根因+优化建议<br>
                • � 趋势图表可视化，一眼看懂数据变化<br>
                • 📄 一键导出专业报表
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_f6:
        st.markdown("""
        <div class="feature-card">
            <div class="value-tag">一个后台管所有店，运营状态一目了然</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">🏢 多店铺总控大屏</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 🖥 一个后台管理所有店铺，不用来回切换<br>
                • 💰 多店盈亏/待办/告警一站式查看<br>
                • 📊 各店数据横向对比，一眼定位问题店<br>
                • ⚡ 跨店铺批量操作，效率翻倍<br>
                • 🔒 数据严格隔离，安全可靠
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==================== 7️⃣ 💰 定价方案 + 💳 收款码 ====================
    st.markdown("## 💎 选择适合你的套餐")

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <div style="margin-bottom: 0.5rem;">
                <span class="user-tag">👤 新手卖家</span>
                <span class="user-tag">📦 单店小卖家</span>
            </div>
            <h3 style="margin-bottom: 0.3rem;">基础版</h3>
            <p style="font-size: 0.82rem; color: #888; margin-bottom: 0.5rem;">搞定利润核算和基础风控，不亏基础钱</p>
            <div class="price-amount" style="color: #333;">¥39.9<span style="font-size: 1.15rem;">/月</span></div>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 1.9; color: #555; margin: 1rem 0; font-size: 0.92rem;">
                ✅ 精准利润计算器（CSV导入+费用拆分）<br>
                ✅ 基础核价自动化（单店核价规则）<br>
                ✅ 库存预警+基础数据分析<br>
                ✅ 7×12小时客服支持<br>
            </ul>
            <a class="cta-button-secondary" style="color: white; text-decoration: none; display: inline-block; pointer-events: none; cursor: not-allowed; opacity: 0.65;" aria-disabled="true">选择基础版</a>
        </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown("""
        <div class="pricing-card popular">
            <div style="margin-bottom: 0.5rem;">
                <span class="user-tag" style="background: rgba(255,255,255,0.2); color: white;">👤 稳定出单卖家</span>
                <span class="user-tag" style="background: rgba(255,255,255,0.2); color: white;">🏪 多店卖家</span>
            </div>
            <h3 style="margin-bottom: 0.3rem;">专业版</h3>
            <p style="font-size: 0.82rem; opacity: 0.85; margin-bottom: 0.5rem;">全流程自动化，实现躺平运营</p>
            <div class="price-amount">¥79.2<span style="font-size: 1.15rem;">/季度</span><br><span class="price-savings">省40%</span></div>
            <p style="font-size: 0.88rem; opacity: 0.9; margin: 0.4rem 0;">原价 ¥99/季度 | 限时8折</p>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 1.9; opacity: 0.95; margin: 1rem 0; font-size: 0.92rem;">
                ✅ 包含所有基础版功能<br>
                ✅ 全自动化模块（核价/库存/调价/活动/消息）<br>
                ✅ 多店铺统一管理+高级数据分析<br>
                ✅ 优先客服支持+专属运营建议<br>
            </ul>
            <p style="font-size: 0.85rem; font-weight: bold; opacity: 0.9; margin-top: 0.5rem;">🔥 90%卖家首选，开启躺平运营的必备方案</p>
            <a class="cta-button-primary" style="color: white; text-decoration: none; display: inline-block; pointer-events: none; cursor: not-allowed; opacity: 0.65;" aria-disabled="true">🎯 立即订阅专业版</a>
        </div>
        """, unsafe_allow_html=True)

    with col_p3:
        st.markdown("""
        <div class="pricing-card">
            <div style="margin-bottom: 0.5rem;">
                <span class="user-tag">👤 长期经营卖家</span>
                <span class="user-tag">👥 团队卖家</span>
            </div>
            <h3 style="margin-bottom: 0.3rem;">终身版</h3>
            <p style="font-size: 0.82rem; color: #888; margin-bottom: 0.5rem;">一劳永逸，永久免费更新</p>
            <div class="price-amount" style="color: #28a745;">¥399<span style="font-size: 1.15rem;"> 一次付费</span></div>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 1.9; color: #555; margin: 1rem 0; font-size: 0.92rem;">
                ✅ 包含所有专业版功能<br>
                ✅ 终身免费更新+新功能优先体验<br>
                ✅ 专属客户经理+定制化需求支持<br>
                ✅ API接口权限+多店无限扩展<br>
            </ul>
            <a class="cta-button-secondary" style="color: white; text-decoration: none; display: inline-block; pointer-events: none; cursor: not-allowed; opacity: 0.65;" aria-disabled="true">🏆 升级终身版</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==================== 💳 收款码与订单表单（保持原有逻辑） ====================
    st.markdown("""<div id="payment-code"></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div class="payment-section">
        <h3 style="text-align: center; color: #333; margin-bottom: 1.2rem; font-size: 1.2rem;">� 选择套餐，立即开通</h3>
        <div style="text-align: center; margin-bottom: 1rem;">
            <span class="guarantee-badge">✅ 7天无理由退款保证 | 不满意全额退款</span>
        </div>
    <p style="text-align: center; color: #666; margin-bottom: 1.2rem; font-size: 0.92rem;">支持微信 / 支付宝，付款后 10 分钟内开通账号</p>
    """, unsafe_allow_html=True)

    if selected_plan:
        plan_info = {
            "basic": {"name": "基础版", "price": "¥39.9/月", "color": "#6c757d"},
            "pro": {"name": "专业版（⭐推荐）", "price": "¥79.2/季度（原价¥99）", "color": "#667eea"},
            "lifetime": {"name": "终身版", "price": "¥399 一次付费", "color": "#28a745"}
        }

        plan = plan_info.get(selected_plan, plan_info["pro"])

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {plan['color']}15 0%, {plan['color']}08 100%);
                    border: 2px solid {plan['color']};
                    padding: 1rem;
                    border-radius: 12px;
                    margin-bottom: 1.5rem;
                    text-align: center;">
            <h3 style="margin: 0 0 0.5rem 0; color: {plan['color']}; font-size: 1.15rem;">
                ✅ 您选择的是：<strong>{plan['name']}</strong>
            </h3>
            <p style="margin: 0; color: {plan['color']}; font-size: 1.3rem; font-weight: bold;">
                💰 {plan['price']}
            </p>
        </div>
        """, unsafe_allow_html=True)

    col_qr1, col_qr2 = st.columns(2)

    with col_qr1:
        st.markdown("""<div class="qr-code-container"><span class="qr-label" style="color: #07C160;">💚 微信支付</span>""", unsafe_allow_html=True)
        try:
            st.image("https://raw.githubusercontent.com/erfengyuzhangsun/temutools/main/WeChat_20260512015412.png", width=230, caption="微信扫码付款")
        except Exception as e:
            st.warning("⚠️ 微信收款码加载失败，请刷新页面或联系客服")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_qr2:
        st.markdown("""<div class="qr-code-container"><span class="qr-label" style="color: #1677FF;">💙 支付宝</span>""", unsafe_allow_html=True)
        try:
            st.image("https://raw.githubusercontent.com/erfengyuzhangsun/temutools/main/paypal_20260512015446.jpg", width=230, caption="支付宝扫码付款")
        except Exception as e:
            st.warning("⚠️ 支付宝收款码加载失败，请刷新页面或联系客服")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background: white; padding: 1.1rem; border-radius: 10px; margin-top: 1.5rem; box-shadow: 0 3px 10px rgba(0,0,0,0.06);">
        <h4 style="color: #333; margin-bottom: 0.8rem; text-align: center; font-size: 1.05rem;">📋 开通流程（简单 4 步）</h4>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 0.6rem;">
            <div style="flex: 1; min-width: 140px; text-align: center; padding: 0.7rem; background: #f8f9fa; border-radius: 8px;">
                <div style="font-size: 1.4rem; margin-bottom: 0.2rem;">1️⃣</div><strong style="font-size: 0.88rem;">选择套餐</strong><br><small style="color: #666; font-size: 0.8rem;">根据需求选择</small>
            </div>
            <div style="flex: 1; min-width: 140px; text-align: center; padding: 0.7rem; background: #f8f9fa; border-radius: 8px;">
                <div style="font-size: 1.4rem; margin-bottom: 0.2rem;">2️⃣</div><strong style="font-size: 0.88rem;">扫码付款</strong><br><small style="color: #666; font-size: 0.8rem;">微信或支付宝</small>
            </div>
            <div style="flex: 1; min-width: 140px; text-align: center; padding: 0.7rem; background: #f8f9fa; border-radius: 8px;">
                <div style="font-size: 1.4rem; margin-bottom: 0.2rem;">3️⃣</div><strong style="font-size: 0.88rem;">发送截图</strong><br><small style="color: #666; font-size: 0.8rem;">发送给客服</small>
            </div>
            <div style="flex: 1; min-width: 140px; text-align: center; padding: 0.7rem; background: #f8f9fa; border-radius: 8px;">
                <div style="font-size: 1.4rem; margin-bottom: 0.2rem;">4️⃣</div><strong style="font-size: 0.88rem;">快速开通</strong><br><small style="color: #666; font-size: 0.8rem;">10分钟内开通</small>
            </div>
        </div>
    </div>

    <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%); padding: 0.85rem; border-radius: 10px; margin-top: 1rem; border-left: 4px solid #ffc107;">
        <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;">
            <span style="font-size: 1.2rem;">⏰</span>
            <div style="font-size: 0.87rem; line-height: 1.5;">
                <strong>服务时间：</strong>周一至周六 9:00-21:00<br>
                <strong>💡 提示：</strong>付款后请备注联系方式（手机号/微信号）
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<h3 style="color: #333; margin-top: 1.5rem; margin-bottom: 1rem; text-align: center; font-size: 1.15rem;">📝 付款后请填写您的联系方式</h3>""", unsafe_allow_html=True)

    with st.form("payment_form"):
        col_form1, col_form2 = st.columns(2)

        with col_form1:
            contact_name = st.text_input("👤 您的姓名 *", placeholder="张三")
            phone = st.text_input("📱 手机号码 *", placeholder="13800138000")

        with col_form2:
            wechat = st.text_input("💬 微信号", placeholder="可选，方便我们联系您")

            plan_options = ["基础版 - ¥39.9/月", "专业版 - ¥79.2/季度（推荐）", "终身版 - ¥399"]
            default_plan = 1 if not selected_plan else (
                0 if selected_plan == "basic" else (1 if selected_plan == "pro" else 2)
            )
            selected_plan_form = st.selectbox(
                "📦 选择套餐 *",
                plan_options,
                index=default_plan
            )

        notes = st.text_area("📝 备注（可选）", placeholder="如有特殊需求请在此说明...")

        submitted = st.form_submit_button(
            "✅ 我已付款，提交订单",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            if not contact_name or not phone:
                st.error("❌ 请填写姓名和手机号！")
            else:
                st.session_state['order_submitted'] = True
                st.session_state['order_info'] = {
                    'name': contact_name,
                    'phone': phone,
                    'wechat': wechat,
                    'plan': selected_plan_form,
                    'notes': notes,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                order_amount = PLAN_PRICES.get(selected_plan_form, 0.0)
                try:
                    save_landing_order(
                        contact_name=contact_name,
                        phone=phone,
                        wechat=wechat or "",
                        plan_name=selected_plan_form,
                        amount=order_amount,
                        notes=notes or ""
                    )
                except Exception as e:
                    print(f"保存订单失败: {e}")

    if st.session_state.get('order_submitted'):
        order = st.session_state.get('order_info', {})
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                    border: 2px solid #28a745;
                    padding: 1.5rem;
                    border-radius: 12px;
                    margin-top: 1.5rem;
                    text-align: center;">
            <h3 style="margin: 0 0 1rem 0; color: #28a745; font-size: 1.4rem;">
                🎉 订单提交成功！
            </h3>
            <p style="margin: 0.5rem 0; color: #155724; font-size: 1rem; line-height: 1.8;">
                感谢您选择 <strong>{order.get('plan', 'Temu全托管自动化运营平台')}</strong>！<br>
                我们将在 <strong style="color: #dc3545;">10分钟内</strong> 通过手机号 <strong>{order.get('phone', '')}</strong> 联系您<br>
                如需加急开通，请添加微信：<strong style="color: #07C160;">returnHuangMuNing</strong>
            </p>
            <p style="margin: 1rem 0 0 0; color: #666; font-size: 0.9rem;">
                ⏰ 订单时间：{order.get('timestamp', '')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📝 提交新订单", use_container_width=True, type="secondary"):
            st.session_state['order_submitted'] = False
            st.session_state['order_info'] = {}
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==================== 8️⃣ 用户评价 ====================
    st.markdown("## 💬 卖家真实反馈")

    st.markdown("""<p style="text-align: center; color: #666; font-size: 0.92rem; margin-bottom: 1.2rem;">已帮助 <strong style="color: #667eea;">800+</strong> 位卖家实现自动化运营</p>""", unsafe_allow_html=True)

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "以前每天运营要花<strong>3小时</strong>，现在全自动化，每天只看5分钟告警，每月多省了100多小时，<strong style="color: #28a745;">单店利润涨了20%</strong>！"
            </p>
            <p style="margin-top: 0.7rem; font-size: 0.9rem;"><strong>— 服装类目卖家 · 张先生</strong> <span style="color: #888;">| 月销500单</span></p>
            <p style="color: #ffc107; font-size: 1rem; margin-top: 0.3rem;">⭐⭐⭐⭐⭐ 使用3个月</p>
        </div>
        """, unsafe_allow_html=True)

    with col_t2:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "自动调价帮我守住了毛利，以前跟价就亏，现在<strong>保毛利前提下自动跟价</strong>，<strong style="color: #28a745;">再也不亏着卖了</strong>！"
            </p>
            <p style="margin-top: 0.7rem; font-size: 0.9rem;"><strong>— 家居类目卖家 · 李女士</strong> <span style="color: #888;">| 月销800单</span></p>
            <p style="color: #ffc107; font-size: 1rem; margin-top: 0.3rem;">⭐⭐⭐⭐⭐ 使用2个月</p>
        </div>
        """, unsafe_allow_html=True)

    col_t3, col_t4 = st.columns(2)

    with col_t3:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "一个后台管5家店，不用来回切换后台，<strong>运营效率直接翻倍</strong>，终于不用熬夜盯数据了！<strong style="color: #667eea;">多店卖家必备</strong>"
            </p>
            <p style="margin-top: 0.7rem; font-size: 0.9rem;"><strong>— 多店卖家 · 陈经理</strong> <span style="color: #888;">| 5家店铺</span></p>
            <p style="color: #ffc107; font-size: 1rem; margin-top: 0.3rem;">⭐⭐⭐⭐⭐ 使用6个月</p>
        </div>
        """, unsafe_allow_html=True)

    with col_t4:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "刚做Temu什么都不懂，工具帮我自动核价、算利润，避开了好几次罚款，<strong style="color: #28a745;">3个月从月亏到月赚3000+</strong>"
            </p>
            <p style="margin-top: 0.7rem; font-size: 0.9rem;"><strong>— 新手卖家 · 王老板</strong> <span style="color: #888;">| 3C数码 | 月销300单</span></p>
            <p style="color: #ffc107; font-size: 1rem; margin-top: 0.3rem;">⭐⭐⭐⭐⭐ 使用1个月</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==================== 9️⃣ 最终 CTA ====================
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])

    with col_cta2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1.2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; color: white; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.35);">
            <h2 style="margin-bottom: 0.6rem; font-size: 1.6rem;">🤖 每天5分钟，告别熬夜运营</h2>
            <p style="margin-bottom: 1.2rem; font-size: 0.95rem; opacity: 0.95; line-height: 1.6;">
                核价、库存、调价、活动、发货全自动搞定<br>
                把时间花在选品和爆单上，而不是盯后台做报表<br>
                <span style="font-size: 0.88rem;">✅ 免费试用 7 天 | ✅ 无需信用卡 | ✅ 随时可取消</span>
            </p>
            <div style="display: flex; gap: 0.6rem; justify-content: center; flex-wrap: wrap;">
                <a href="?page=app" class="cta-button-primary" style="color: white; text-decoration: none;">� 免费试用7天 →</a>
                <a href="#payment-code" class="cta-button-outline" style="color: white; text-decoration: none;">💰 查看定价方案</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==================== 🔟 FAQ + 联系方式 ====================
    col_faq1, col_faq2 = st.columns([1, 1])

    with col_faq1:
        st.markdown("<div class='faq-section'>", unsafe_allow_html=True)
        st.markdown("### ❓ 你对自动化最关心的问题")

        faq_data = [
            ("Q: 自动化核价会不会误处理，导致我亏损？",
             "A: 所有核价操作都按你预设的毛利规则执行，支持日常/活动双阈值，可手动干预，操作全留日志可溯源，<strong>不会误处理</strong>。"),
            ("Q: 数据安全吗？会不会泄露我的店铺数据？",
             "A: 店铺数据本地加密存储，API密钥不上云，所有操作留日志可溯源，<strong>不会上传你的店铺隐私数据</strong>。"),
            ("Q: 多店铺支持吗？会不会操作混乱？",
             "A: 支持多店铺统一管理，一个后台查看所有店铺的盈亏、待办和告警，<strong>数据严格隔离，不会混乱</strong>。"),
            ("Q: 我是新手，不会用怎么办？",
             "A: 提供详细的使用教程+专属客服支持，<strong>7×12小时在线答疑</strong>，新手也能快速上手。")
        ]

        for question, answer in faq_data:
            st.markdown(f"""
            <div class="faq-item">
                <div class="faq-question">{question}</div>
                <div class="faq-answer">{answer}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_faq2:
        st.markdown("<div class='faq-section'>", unsafe_allow_html=True)
        st.markdown("### 📞 联系我们")

        contact_data = [
            ("💬 微信客服", "returnHuangMuNing", '添加好友后发送「咨询」即可', "#07C160"),
            ("📧 邮箱联系", "484478363@qq.com", "24小时内回复", "#667eea"),
            ("⏰ 工作时间", "周一至周六 9:00 - 21:00", "节假日可能延迟回复", "#333")
        ]

        for title, value, note, color in contact_data:
            st.markdown(f"""
            <div class="contact-card">
                <div class="contact-title">{title}</div>
                <div class="contact-value" style="color: {color};">{value}</div>
                <div class="contact-note">{note}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; padding: 1.2rem 0; margin-top: 1.5rem; border-top: 2px solid #e9ecef; color: #888;">
        <p style="margin: 0.3rem 0; font-size: 0.88rem;">© 2026 Temu全托管自动化运营平台 | 告别熬夜盯后台，Temu运营交给AI 🤖</p>
        <p style="margin: 0.3rem 0; font-size: 0.8rem; color: #aaa;">本工具仅用于辅助商家进行数据分析和运营决策，不构成任何投资建议</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show_landing_page()

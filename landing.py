import streamlit as st
from datetime import datetime

def show_landing_page():
    st.set_page_config(
        page_title="Temu 商家风控与利润管家 - 产品首页",
        page_icon="💰",
        layout="wide"
    )
    
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
            content: '⭐ 最受欢迎';
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
        
        /* ========== 痛点/解决方案卡片（超紧凑） ========== */
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
        }
        
        /* ========== 隐藏 Streamlit 默认元素 ========== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* ========== 滚动条美化 ========== */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)
    
    # ==================== 1️⃣ Hero Section（超紧凑） ====================
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">💰 Temu 商家风控与利润管家</div>
        <div class="hero-subtitle">
            精确到分的费用拆分 | 实时亏损预警 | 智能罚款预测<br>
            <span style="font-size: 0.95rem; opacity: 0.85;">让每个 Temu 卖家都能赚到钱 💪</span>
        </div>
        <div style="margin-top: 1.2rem; position: relative; z-index: 1;">
            <a href="?page=app" class="cta-button-primary" style="color: white; text-decoration: none;">🚀 免费试用 7 天 →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== 2️⃣ 紧迫感横幅（超紧凑） ====================
    st.markdown("""
    <div class="urgency-banner">
        <h3 style="margin: 0 0 0.3rem 0; font-size: 1.15rem;">🎉 首发特惠：前 <strong>100</strong> 名用户享受 <strong>8折优惠</strong></h3>
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
        st.markdown("""<div class="stat-item"><div class="stat-number">500+</div><div class="stat-label">👥 位卖家在使用</div></div>""", unsafe_allow_html=True)
    
    with col_s2:
        st.markdown("""<div class="stat-item"><div class="stat-number">¥200万+</div><div class="stat-label">💰 累计避免罚款</div></div>""", unsafe_allow_html=True)
    
    with col_s3:
        st.markdown("""<div class="stat-item"><div class="stat-number">98%</div><div class="stat-label">⭐ 用户满意度</div></div>""", unsafe_allow_html=True)
    
    with col_s4:
        st.markdown("""<div class="stat-item"><div class="stat-number">4.9/5</div><div class="stat-label">💬 用户评分</div></div>""", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ==================== 4️⃣ 痛点 vs 解决方案 ====================
    col_pain, col_solution = st.columns(2)
    
    with col_pain:
        st.markdown("### 😰 Temu 卖家的痛点")
        st.markdown("""
        <div class="pain-point"><strong>❌ 费用看不懂</strong><br>平台扣费有10多项：基础佣金5%-11%、物流费、支付处理费1.75%+$0.12/单...</div>
        <div class="pain-point"><strong>❌ 利润算不清</strong><br>日出几十单，月底一算反而亏了几千块，很多SKU其实在亏钱却不知道</div>
        <div class="pain-point"><strong>❌ 罚款防不住</strong><br>发货超时、虚假发货、货不对版...各种罚款突如其来，防不胜防</div>
        <div class="pain-point"><strong>❌ 风险不知道</strong><br>不知道哪些SKU在亏钱，不知道什么时候会被罚款</div>
        """, unsafe_allow_html=True)
    
    with col_solution:
        st.markdown("### ✅ 我们的解决方案")
        st.markdown("""
        <div class="solution-point"><strong>✅ 精确费用拆分</strong><br>自动拆分每一项费用，精确到每个订单、每个SKU，一目了然</div>
        <div class="solution-point"><strong>✅ 真实利润计算</strong><br>不是理论利润，是扣除所有费用后实际能到手多少钱</div>
        <div class="solution-point"><strong>✅ 智能风险预警</strong><br>6大风险指标实时监控，提前3天预警避免罚款</div>
        <div class="solution-point"><strong>✅ 数据驱动决策</strong><br>告诉你哪些SKU赚钱该加大投入，哪些亏钱该立即下架</div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== 5️⃣ 核心功能展示 ====================
    st.markdown("## 🎯 核心功能")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea; margin-bottom: 0.7rem; font-size: 1.15rem;">📊 精准利润计算器</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 🔄 一键导入订单CSV<br>
                • 🔍 自动拆分10+项费用<br>
                • 💵 计算真实净利润<br>
                • 📦 SKU级利润分析<br>
                • ⚠️ 利润率低于5%自动预警
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_f2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea; margin-bottom: 0.7rem; font-size: 1.15rem;">⚠️ 智能风险监控</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 📈 6大核心指标实时监控<br>
                • 🚨 多级预警系统（黄/红）<br>
                • 📊 风险仪表盘可视化<br>
                • 💡 智能改进建议<br>
                • 🔮 罚款金额预测
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_f3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea; margin-bottom: 0.7rem; font-size: 1.15rem;">📈 数据分析报告</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • ⭐ 店铺健康评分（A-F）<br>
                • 🥧 费用构成饼图<br>
                • 🏆 SKU盈利排行榜<br>
                • 📉 风险趋势分析<br>
                • 📄 一键导出Excel报表
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== 6️⃣ 💰 定价方案 + 💳 收款码 ====================
    st.markdown("## 💎 选择适合你的套餐")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="margin-bottom: 0.7rem;">基础版</h3>
            <div class="price-amount" style="color: #333;">¥39.9<span style="font-size: 1.15rem;">/月</span></div>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 1.9; color: #555; margin: 1rem 0; font-size: 0.92rem;">
                ✅ 利润计算功能<br>✅ 基础费用拆分<br>✅ CSV数据导入<br>✅ 导出基础报表<br>❌ 风险预警系统<br>❌ 高级数据分析
            </ul>
            <a href="?page=landing&plan=basic#payment" class="cta-button-secondary" style="color: white; text-decoration: none; display: inline-block;">选择基础版</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col_p2:
        st.markdown("""
        <div class="pricing-card popular">
            <h3 style="margin-bottom: 0.7rem;">专业版</h3>
            <div class="price-amount">¥79.2<span style="font-size: 1.15rem;">/季度</span><br><span class="price-savings">省40%</span></div>
            <p style="font-size: 0.88rem; opacity: 0.9; margin: 0.4rem 0;">原价 ¥99/季度 | 限时8折</p>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 1.9; margin: 1rem 0; font-size: 0.92rem;">
                ✅ 所有基础版功能<br>✅ 完整风险预警系统<br>✅ 6大指标实时监控<br>✅ 高级数据分析报告<br>✅ SKU级深度分析<br>✅ 优先客服支持
            </ul>
            <a href="?page=landing&plan=pro#payment" class="cta-button-primary" style="background: white !important; color: #667eea !important; display: inline-block; text-decoration: none;">⭐ 立即开通</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col_p3:
        st.markdown("""
        <div class="pricing-card">
            <h3 style="margin-bottom: 0.7rem;">终身版</h3>
            <div class="price-amount" style="color: #333;">¥399<span style="font-size: 1.15rem;">一次付费</span></div>
            <p style="font-size: 0.88rem; color: #28a745; font-weight: bold; margin: 0.4rem 0;">最超值选择！</p>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 1.9; color: #555; margin: 1rem 0; font-size: 0.92rem;">
                ✅ 所有专业版功能<br>✅ 终身免费更新<br>✅ 新功能优先体验<br>✅ 专属客户经理<br>✅ 定制化需求支持<br>✅ API接口权限
            </ul>
            <a href="?page=landing&plan=lifetime#payment" class="cta-button-secondary" style="background: #28a745 !important; color: white !important; display: inline-block; text-decoration: none;">购买终身版</a>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== 💳 扫码付款区域 ====================
    st.markdown("<div class='payment-section' id='payment'>", unsafe_allow_html=True)
    
    st.markdown("""
    <h2 style="text-align: center; color: #333; margin-bottom: 0.2rem; font-size: 1.35rem;">📱 扫码付款，立即开通</h2>
    <p style="text-align: center; color: #666; margin-bottom: 1.2rem; font-size: 0.92rem;">支持微信 / 支付宝，付款后 10 分钟内开通账号</p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <span class="guarantee-badge">✅ 7天无理由退款保证 | 不满意全额退款</span>
    </div>
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
                感谢您选择 <strong>{order.get('plan', 'Temu 商家风控与利润管家')}</strong>！<br>
                我们将在 <strong style="color: #dc3545;">10分钟内</strong> 通过手机号 <strong>{order.get('phone', '')}</strong> 联系您<br>
                如需加急开通，请添加微信：<strong style="color: #07C160;">temu_tools_helper</strong>
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
    
    # ==================== 7️⃣ 用户评价（超紧凑版） ====================
    st.markdown("## 💬 用户真实评价")
    
    st.markdown("""<p style="text-align: center; color: #666; font-size: 0.92rem; margin-bottom: 1.2rem;">已帮助 <strong style="color: #667eea;">500+</strong> 位卖家提升利润</p>""", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "用了这个工具才发现，我之前有好几个SKU一直在亏钱！现在每个月能多赚<strong style="color: #28a745;">2000多块</strong>，真的太值了！"
            </p>
            <p style="margin-top: 0.7rem; font-size: 0.9rem;"><strong>— 张先生</strong> <span style="color: #888;">| 服装类目 | 月销500单</span></p>
            <p style="color: #ffc107; font-size: 1rem; margin-top: 0.3rem;">⭐⭐⭐⭐⭐ 使用3个月</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t2:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "最怕的就是被罚款，这个工具<strong style="color: #dc3545;">提前3天就预警</strong>了我的发货超时问题，帮我避免了<strong style="color: #28a745;">5000多的罚款</strong>！"
            </p>
            <p style="margin-top: 0.7rem; font-size: 0.9rem;"><strong>— 李女士</strong> <span style="color: #888;">| 家居百货 | 月销800单</span></p>
            <p style="color: #ffc107; font-size: 1rem; margin-top: 0.3rem;">⭐⭐⭐⭐⭐ 使用2个月</p>
        </div>
        """, unsafe_allow_html=True)
    
    col_t3, col_t4 = st.columns(2)
    
    with col_t3:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "作为一个新手卖家，之前完全搞不懂费用结构。这个工具让我<strong style="color: #667eea;">一目了然</strong>地看到每一笔钱的去向，利润率从3%提升到了<strong style="color: #28a745;">12%</strong>！"
            </p>
            <p style="margin-top: 0.7rem; font-size: 0.9rem;"><strong>— 王老板</strong> <span style="color: #888;">| 3C数码 | 月销300单</span></p>
            <p style="color: #ffc107; font-size: 1rem; margin-top: 0.3rem;">⭐⭐⭐⭐⭐ 使用1个月</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t4:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "客服响应很快，问题都能及时解决。<strong style="color: #667eea;">每周更新费用规则</strong>这点太重要了，再也不怕平台悄悄改规则了！"
            </p>
            <p style="margin-top: 0.7rem; font-size: 0.9rem;"><strong>— 陈经理</strong> <span style="color: #888;">| 美妆类目 | 月销1200单</span></p>
            <p style="color: #ffc107; font-size: 1rem; margin-top: 0.3rem;">⭐⭐⭐⭐⭐ 使用6个月</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== 8️⃣ 最终 CTA（超紧凑） ====================
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    
    with col_cta2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1.2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; color: white; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.35);">
            <h2 style="margin-bottom: 0.6rem; font-size: 1.6rem;">🚀 别再让隐形亏损吞噬你的利润！</h2>
            <p style="margin-bottom: 1.2rem; font-size: 0.95rem; opacity: 0.95; line-height: 1.6;">
                上传CSV，<strong>30秒</strong>获取完整分析报告<br>
                发现隐藏的亏损点，<strong>每月多赚数千元</strong><br>
                <span style="font-size: 0.88rem;">✅ 免费试用 7 天 | ✅ 无需信用卡 | ✅ 随时可取消</span>
            </p>
            <div style="display: flex; gap: 0.6rem; justify-content: center; flex-wrap: wrap;">
                <a href="?page=app" class="cta-button-primary" style="color: white; text-decoration: none;">📊 免费试用 →</a>
                <a href="#pricing" class="cta-button-secondary" style="color: white; text-decoration: none;">💰 查看定价</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== 9️⃣ FAQ + 联系方式（完全修复HTML泄露） ====================
    col_faq1, col_faq2 = st.columns([1, 1])
    
    with col_faq1:
        st.markdown("<div class='faq-section'>", unsafe_allow_html=True)
        st.markdown("### ❓ 常见问题")
        
        faq_data = [
            ("Q: 支持哪些数据格式？", "A: 支持从 Temu 商家后台直接导出的 CSV 文件，包含订单明细和结算数据"),
            ("Q: 数据安全吗？", "A: ✅ **绝对安全！** 所有数据仅在您的本地浏览器处理，**不会上传到我们的服务器**。您的数据完全由您自己掌控。"),
            ("Q: 费用规则会更新吗？", "A: ✅ 是的！我们**每周更新** Temu 最新费用规则，确保计算结果始终准确。这是我们的核心竞争力之一！"),
            ("Q: 如何联系客服？", "A: 微信：**temu_tools_helper** 或邮箱：**484478363@qq.com**，工作时间内 10 分钟内回复")
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
            ("💬 微信客服", "temu_tools_helper", '添加好友后发送「咨询」即可', "#07C160"),
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
    
    # 页脚（超紧凑）
    st.markdown("""
    <div style="text-align: center; padding: 1.2rem 0; margin-top: 1.5rem; border-top: 2px solid #e9ecef; color: #888;">
        <p style="margin: 0.3rem 0; font-size: 0.88rem;">© 2026 Temu 商家风控与利润管家 | 让每个卖家都能赚到钱 💪</p>
        <p style="margin: 0.3rem 0; font-size: 0.8rem; color: #aaa;">本工具仅用于辅助商家进行数据分析和决策，不构成任何投资建议</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show_landing_page()

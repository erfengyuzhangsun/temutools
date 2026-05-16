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
            page_title="跨境卖家运营辅助工具 - 高效运营助手",
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
        * { box-sizing: border-box; }
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
        .urgency-banner {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 0.8rem 1.2rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(255, 107, 107, 0.25);
        }
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
        .faq-question { color: #333; font-weight: bold; font-size: 0.92rem; margin-bottom: 0.3rem; }
        .faq-answer { color: #555; font-size: 0.87rem; line-height: 1.5; }
        .contact-card {
            background: white;
            padding: 0.85rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        }
        .contact-title { font-size: 0.92rem; color: #333; font-weight: bold; margin-bottom: 0.3rem; }
        .contact-value { font-size: 0.98rem; font-weight: bold; color: #667eea; }
        .contact-note { font-size: 0.8rem; color: #888; margin-top: 0.2rem; }
        .user-tag {
            display: inline-block;
            background: #e9ecef;
            padding: 0.15rem 0.6rem;
            border-radius: 8px;
            font-size: 0.78rem;
            color: #555;
            margin: 0.2rem;
        }
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
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 4px; }
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
        .stSidebar * { color: #1E1E1E !important; }
        input, textarea, select, [data-baseweb="input"] input {
            background-color: #FFFFFF !important;
            color: #1E1E1E !important;
        }
        .css-1y4p8pa, .css-1r6goiv, .css-1v3fvcr, .css-1x8cf1d,
        .css-1n76uvr, .css-1cpxqw2, .css-1q8ddro { color: #1E1E1E !important; }
        [data-testid="baseButton-secondary"] { color: #1E1E1E !important; }
        .demo-section {
            background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
            border-radius: 16px;
            padding: 1.8rem 1.5rem;
            margin: 1.5rem 0;
            border: 2px solid #d0d5ff;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.12);
        }
        .demo-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
        }
        .demo-card {
            background: white;
            border-radius: 12px;
            padding: 1rem 0.9rem;
            box-shadow: 0 3px 12px rgba(0,0,0,0.06);
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
            position: relative;
        }
        .demo-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.18);
        }
        .demo-num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            font-size: 0.8rem;
            font-weight: bold;
            margin-bottom: 0.4rem;
        }
        .demo-card h4 { margin: 0.3rem 0 0.3rem 0; font-size: 1rem; }
        .demo-card p { margin: 0; font-size: 0.85rem; color: #555; line-height: 1.5; }
        @media (max-width: 768px) {
            .demo-grid { grid-template-columns: 1fr; }
        }
        .demo-carousel {
            background: white;
            border-radius: 14px;
            padding: 1.5rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            margin-bottom: 1rem;
        }
        .demo-step-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .demo-step-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            font-size: 0.9rem;
            font-weight: bold;
            flex-shrink: 0;
        }
        .mock-ui {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            position: relative;
        }
        .mock-ui-header {
            background: linear-gradient(135deg, #f0f2f5 0%, #e8ecf0 100%);
            padding: 0.6rem 1rem;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.85rem;
            font-weight: 600;
            color: #444;
        }
        .mock-ui-header .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }
        .mock-ui-header .dot-red { background: #ff5f56; }
        .mock-ui-header .dot-yellow { background: #ffbd2e; }
        .mock-ui-header .dot-green { background: #27c93f; }
        .mock-ui-body { padding: 1rem 1.2rem; min-height: 200px; position: relative; }
        .mock-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
        .mock-table th { background: #f8f9fa; padding: 0.5rem 0.6rem; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #e0e0e0; }
        .mock-table td { padding: 0.45rem 0.6rem; border-bottom: 1px solid #f0f0f0; color: #333; }
        .mock-table tr:hover td { background: #f8f9ff; }
        .mock-tag { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
        .mock-tag-success { background: #d4edda; color: #155724; }
        .mock-tag-warning { background: #fff3cd; color: #856404; }
        .mock-tag-danger { background: #f8d7da; color: #721c24; }
        .mock-tag-info { background: #d1ecf1; color: #0c5460; }
        .mock-panel { background: #f8f9ff; border: 1px solid #e8ecf0; border-radius: 8px; padding: 0.8rem 1rem; margin-top: 0.6rem; }
        .mock-panel-title { font-size: 0.8rem; font-weight: 600; color: #667eea; margin-bottom: 0.4rem; }
        .mock-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem; font-size: 0.82rem; }
        .mock-label { color: #666; }
        .mock-value { font-weight: 600; color: #333; }
        .mock-highlight { background: #fff8e1; border-left: 3px solid #ffc107; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.82rem; }
        .mock-highlight-red { background: #fff0f0; border-left: 3px solid #dc3545; padding: 0.3rem 0.6rem; border-radius: 4px; color: #721c24; font-size: 0.82rem; }
        .mock-btn { display: inline-block; padding: 0.35rem 1rem; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; border: none; }
        .mock-btn-primary { background: #667eea; color: white; }
        .mock-btn-success { background: #28a745; color: white; }
        .mock-btn-outline { background: transparent; border: 1px solid #667eea; color: #667eea; }
        .annotation { position: relative; display: flex; align-items: flex-start; gap: 0.5rem; margin-top: 0.9rem; padding: 0.6rem 0.8rem; background: #f0f4ff; border-radius: 8px; border: 1px dashed #667eea; }
        .annotation-arrow { flex-shrink: 0; width: 28px; height: 28px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; }
        .annotation-text { font-size: 0.85rem; color: #444; line-height: 1.5; }
        .annotation-text strong { color: #667eea; }
        .mock-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        @media (max-width: 600px) { .mock-two-col { grid-template-columns: 1fr; } }
        .mock-col { background: #fafbfc; border: 1px solid #eee; border-radius: 8px; padding: 0.8rem; }
        .mock-col-title { font-size: 0.8rem; font-weight: 600; color: #667eea; margin-bottom: 0.5rem; padding-bottom: 0.3rem; border-bottom: 1px solid #e0e0e0; }
        .step-indicator { display: flex; justify-content: center; align-items: center; gap: 0.6rem; margin: 1rem 0; }
        .step-dot { width: 10px; height: 10px; border-radius: 50%; background: #d0d5ff; transition: all 0.3s ease; cursor: pointer; }
        .step-dot.active { width: 32px; border-radius: 6px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .step-dot:hover:not(.active) { background: #b0b8ff; }
        .step-label { font-size: 0.8rem; color: #999; text-align: center; margin-top: 0.3rem; }
        .step-label.active { color: #667eea; font-weight: 600; }
        .demo-footer-text { text-align: center; padding: 0.8rem 1rem; background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%); border-radius: 10px; font-size: 0.95rem; color: #444; margin-top: 1rem; border: 1px solid #d0d5ff; }
        .demo-footer-text strong { color: #667eea; }
        .annotations-group { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.8rem; }
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
        <div style="font-size: 0.85rem; opacity: 0.8; margin-bottom: 0.4rem; position: relative; z-index: 1;">🤖 跨境卖家运营辅助工具</div>
        <div class="hero-title">智能运营辅助<br>让数据帮你做决策，高效管理店铺</div>
        <div class="hero-subtitle">
            核价、库存、调价、活动、发货、售后一站式管理<br>
            <strong>提升运营效率，省时省力</strong>
        </div>
        <div style="margin-top: 1rem; position: relative; z-index: 1; display: flex; gap: 0.8rem; justify-content: center; flex-wrap: wrap;">
            <a href="?page=app" class="cta-button-primary" style="color: white; text-decoration: none;">🚀 免费试用7天，开启高效运营</a>
        </div>
        <div style="margin-top: 1rem; display: flex; gap: 1.2rem; justify-content: center; flex-wrap: wrap; position: relative; z-index: 1; font-size: 0.82rem; opacity: 0.9;">
            <span>✅ 助力卖家简化日常运营流程</span>
            <span>✅ 功能覆盖核价/库存/调价/活动/消息</span>
            <span>✅ 数据加密存储，保障信息安全</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_enter1, col_enter2, col_enter3, col_enter4 = st.columns([1, 1.5, 0.3, 1.5])
    with col_enter2:
        if st.button("🚪 进入应用", use_container_width=True, type="primary"):
            st.session_state["page"] = "app"
            st.query_params["page"] = "app"
    with col_enter4:
        if st.button("▶ 查看全功能演示", use_container_width=True, type="secondary"):
            st.session_state["show_demo"] = True

    # ==================== 1.5️⃣ 全功能演示（10步，覆盖全部模块） ====================
    show_demo = st.session_state.get("show_demo", False)
    if show_demo:
        st.session_state["show_demo"] = True
        if "demo_step" not in st.session_state:
            st.session_state["demo_step"] = 1
        current_step = st.session_state["demo_step"]

        st.markdown("""
        <div class="demo-section">
            <div style="text-align: center; margin-bottom: 1.2rem;">
                <h3 style="margin: 0; font-size: 1.35rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">🤖 全功能演示 · 共10步</h3>
                <p style="color: #555; margin: 0.4rem 0 0 0; font-size: 0.92rem;">覆盖运营全流程，无论是否接入API均可使用</p>
            </div>
        """, unsafe_allow_html=True)

        _step_names = ["API密钥获取指引", "工厂成本管理", "全托管核价引擎", "风控防二次核价", "自动核价处理", "智能调价管理", "库存预警管理", "活动自动报名", "消息与售后管理", "数据大屏与报表"]
        _step_icons = ["🔑", "🏭", "🧮", "🛡️", "📊", "⚡", "🚨", "🎯", "💬", "📈"]
        _step_title = f"步骤{current_step}：{_step_icons[current_step-1]} {_step_names[current_step-1]}"

        # ────────── Step 1: API密钥获取指引 ──────────
        if current_step == 1:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">🔑 API密钥管理 — 三步获取你的店铺密钥</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">📋 密钥获取3步骤</div>
                                <div style="margin: 0.5rem 0;">
                                    <div style="padding:0.5rem; background:#e8f4fd; border-radius:8px; margin-bottom:0.5rem;">
                                        <strong>Step 1</strong> — 登录卖家中心 → 服务市场 → 自研应用管理
                                    </div>
                                    <div style="padding:0.5rem; background:#e8f4fd; border-radius:8px; margin-bottom:0.5rem;">
                                        <strong>Step 2</strong> — 创建自研应用，等待审核通过
                                    </div>
                                    <div style="padding:0.5rem; background:#e8f4fd; border-radius:8px; margin-bottom:0.5rem;">
                                        <strong>Step 3</strong> — 复制 App Key + App Secret + Access Token
                                    </div>
                                    <div style="margin-top:0.5rem; font-size:0.8rem; color:#888;">
                                        不会操作？进入应用后打开「API密钥管理」页面有完整图文教程
                                    </div>
                                </div>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">🔐 填入密钥一键保存</div>
                                <div style="margin: 0.5rem 0;">
                                    <div style="padding:0.4rem 0.6rem; background:#f0f0f0; border-radius:6px; margin-bottom:0.3rem;">
                                        App Key:  <strong style="color:#667eea;">•••••a3f8</strong>
                                    </div>
                                    <div style="padding:0.4rem 0.6rem; background:#f0f0f0; border-radius:6px; margin-bottom:0.3rem;">
                                        App Secret: <strong style="color:#667eea;">•••••f7d2</strong>
                                    </div>
                                    <div style="padding:0.4rem 0.6rem; background:#f0f0f0; border-radius:6px; margin-bottom:0.3rem;">
                                        Access Token: <strong style="color:#667eea;">•••••e4b1</strong>
                                    </div>
                                    <div style="margin-top:0.5rem; padding:0.4rem; background:#d4edda; border-radius:6px; font-size:0.82rem; color:#155724;">
                                        ✅ 加密存储，安全可靠，系统自动使用
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>不会API密钥申请？</strong> — 进入应用后「API密钥管理」页有完整的图文指引，逐步骤教你在卖家中心申请密钥，10分钟搞定</div>
                    </div>
                    <div class="annotation">
                        <div class="annotation-arrow">②</div>
                        <div class="annotation-text"><strong>没有密钥也能用！</strong> — 系统内置模拟数据模式，不填密钥即可体验全部功能，填了密钥自动切换为真实数据</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>提示：</strong>系统中所有API密钥使用加密存储，安全可靠。无密钥也可使用Mock模式体验全部功能
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 2: 工厂成本管理 ──────────
        elif current_step == 2:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">🏭 工厂成本管理 — 产品资料录入与供货价测算</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">📋 产品录入表</div>
                                <table class="mock-table">
                                    <tr><th>SKU</th><th>产品名称</th><th>材料成本</th><th>人工</th><th>包装</th><th>总成本</th></tr>
                                    <tr><td>C001</td><td>智能保温杯</td><td>¥12.50</td><td>¥3.00</td><td>¥1.50</td><td>¥18.50</td></tr>
                                    <tr><td>C002</td><td>无线充电器</td><td>¥22.00</td><td>¥4.50</td><td>¥2.00</td><td>¥29.80</td></tr>
                                    <tr><td>C003</td><td>运动腰包</td><td>¥8.00</td><td>¥5.00</td><td>¥1.20</td><td>¥15.00</td></tr>
                                </table>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">💰 自动算价结果</div>
                                <div class="mock-panel">
                                    <div class="mock-row"><span class="mock-label">SKU-C001 期望毛利</span><span class="mock-value">25%</span></div>
                                    <div class="mock-row"><span class="mock-label">建议供货价</span><span class="mock-value" style="color:#28a745;">¥23.13</span></div>
                                    <div class="mock-row"><span class="mock-label">SKU-C002 期望毛利</span><span class="mock-value">30%</span></div>
                                    <div class="mock-row"><span class="mock-label">建议供货价</span><span class="mock-value" style="color:#28a745;">¥38.74</span></div>
                                </div>
                                <div style="margin-top:0.5rem;text-align:center;">
                                    <span class="mock-btn mock-btn-success" style="font-size:0.82rem;">📤 导出核价报表Excel</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>录入产品成本明细</strong> — 填入材料、人工、包装、运费等各项成本，系统自动计算总成本</div>
                    </div>
                    <div class="annotation">
                        <div class="annotation-arrow">②</div>
                        <div class="annotation-text"><strong>自动建议供货价</strong> — 按你设定的期望毛利率自动计算建议供货价，支持一键导出核价分析报表</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>工厂卖家精准掌握产品成本，确保供货价合理有利润
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 3: 全托管核价引擎 ──────────
        elif current_step == 3:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">🧮 全托管核价引擎 — 纯算法，零API依赖</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">📊 成本→供货价测算</div>
                                <div class="mock-panel">
                                    <div class="mock-row"><span class="mock-label">总成本</span><span class="mock-value">¥18.50</span></div>
                                    <div class="mock-row"><span class="mock-label">目标毛利率</span><span class="mock-value">25%</span></div>
                                    <div class="mock-row"><span class="mock-label">建议供货价</span><span class="mock-value" style="color:#28a745;font-weight:bold;">¥23.13</span></div>
                                    <div class="mock-row"><span class="mock-label">净利润</span><span class="mock-value" style="color:#28a745;">¥4.63</span></div>
                                    <div class="mock-row"><span class="mock-label">安全调价上限</span><span class="mock-value">¥27.75</span></div>
                                    <div class="mock-row"><span class="mock-label">安全调价下限</span><span class="mock-value" style="color:#dc3545;">¥20.82</span></div>
                                </div>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">⚙️ 规则设置</div>
                                <div class="mock-panel">
                                    <div class="mock-row"><span class="mock-label">全托管模式</span><span class="mock-value">✅ 已选</span></div>
                                    <div class="mock-row"><span class="mock-label">平台佣金</span><span class="mock-value">5.5%</span></div>
                                    <div class="mock-row"><span class="mock-label">平台扣点</span><span class="mock-value">0.6%</span></div>
                                    <div class="mock-row"><span class="mock-label">调价风控评估</span><span class="mock-value" style="color:#28a745;">✅ 通过</span></div>
                                </div>
                                <div style="margin-top:0.5rem;text-align:center;">
                                    <span class="mock-btn mock-btn-primary" style="font-size:0.85rem;">📊 批量分析多个SKU</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>纯算法引擎</strong> — 不依赖API，输入成本即可自动计算供货价、净利润、安全调价区间</div>
                    </div>
                    <div class="annotation">
                        <div class="annotation-arrow">②</div>
                        <div class="annotation-text"><strong>全托管/半托管独立规则</strong> — 两种模式采用不同的佣金扣点计算逻辑，精准算出净利润</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>零API依赖，输入成本即出建议供货价，辅助核价决策
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 4: 风控防二次核价 ──────────
        elif current_step == 4:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">🛡️ 风控规则引擎 — 调价前自动检测风险</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #dc3545; background: #fff5f5;">
                                <div class="mock-col-title" style="color: #dc3545; font-weight: 700;">⚠️ 本次调价拦截报告</div>
                                <div class="mock-highlight-red" style="margin-bottom:0.4rem;">
                                    <strong>🚫 规则R001：毛利率低于安全线</strong><br>调价后毛利率12.5% < 安全线15.0%
                                </div>
                                <div class="mock-highlight-red" style="margin-bottom:0.4rem;">
                                    <strong>🚫 规则R003：频繁调价触发风控</strong><br>24小时内调价3次 > 最大允许2次
                                </div>
                                <div style="margin-top:0.5rem;font-size:0.82rem;color:#dc3545;">
                                    ⛔ 本次调价已被风控系统拦截
                                </div>
                            </div>
                            <div class="mock-col" style="border: 2px solid #28a745; background: #f5fff5;">
                                <div class="mock-col-title" style="color: #28a745; font-weight: 700;">📋 风控规则（6条内置）</div>
                                <div style="margin-bottom:0.3rem;font-size:0.82rem;">✅ R001 毛利率低于安全线 — 已开启</div>
                                <div style="margin-bottom:0.3rem;font-size:0.82rem;">✅ R002 单次调价幅度超限 — 已开启</div>
                                <div style="margin-bottom:0.3rem;font-size:0.82rem;">✅ R003 频繁调价触发风控 — 已开启</div>
                                <div style="font-size:0.82rem;">✅ R004/R005/R006 其他规则 — 已开启</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>先审后调，不亏一分钱</strong> — 任何调价操作前，6条风控规则逐一检测，命中任意规则立即拦截并注明原因</div>
                    </div>
                    <div class="annotation">
                        <div class="annotation-arrow">②</div>
                        <div class="annotation-text"><strong>防止二次核价风险</strong> — 核心规则R001专为全托管卖家设计，防止毛利率过低导致平台二次核价压价</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>全部调价操作先过风控再执行，守住利润底线的精准利润掌控
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 5: 自动核价 ──────────
        elif current_step == 5:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">📊 核价自动化 — 核价通知管理与自动处理</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">📋 核价通知列表 <span style="float:right;font-size:0.75rem;color:#999;font-weight:400;">共 3 条待处理</span></div>
                                <table class="mock-table">
                                    <tr><th>SKU</th><th>平台报价</th><th>成本价</th><th>利润率</th><th>状态</th></tr>
                                    <tr><td>SKU-A1001</td><td>¥100.00</td><td>¥80.00</td><td>25.0%</td><td><span class="mock-tag mock-tag-success">✅ 接受</span></td></tr>
                                    <tr><td>SKU-B2003</td><td>¥85.00</td><td>¥75.00</td><td>13.3%</td><td><span class="mock-tag mock-tag-danger">⚠️ 低于阈值</span></td></tr>
                                    <tr><td>SKU-C3005</td><td>¥120.00</td><td>¥95.00</td><td>26.3%</td><td><span class="mock-tag mock-tag-success">✅ 接受</span></td></tr>
                                </table>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">⚙️ 毛利率规则设置</div>
                                <div class="mock-panel">
                                    <div class="mock-row"><span class="mock-label">常规商品阈值</span><span class="mock-value">20.0%</span></div>
                                    <div class="mock-row"><span class="mock-label">活动商品阈值</span><span class="mock-value">10.0%</span></div>
                                    <div class="mock-row"><span class="mock-label">超时自动处理</span><span class="mock-value">✅ 开启</span></div>
                                    <div class="mock-row"><span class="mock-label">处理策略</span><span class="mock-value">高于阈值自动接受</span></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>按你预设的保本规则自动算价</strong> — 高于阈值自动接受，低于阈值自动拦截，不再手动算价</div>
                    </div>
                    <div class="annotation">
                        <div class="annotation-arrow">②</div>
                        <div class="annotation-text"><strong>超时未处理强提醒</strong> — 核价通知即将超时时自动提醒，拒绝亏损价、不遗漏</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>系统批量处理核价通知，拒绝亏损价，节省运营时间
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 6: 智能调价 ──────────
        elif current_step == 6:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">⚡ 智能调价 — 竞品监控与自动跟价</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">📊 竞品价格监控 <span style="float:right;font-size:0.75rem;color:#999;">更新于30秒前</span></div>
                                <table class="mock-table">
                                    <tr><th>SKU</th><th>你的售价</th><th>竞品售价</th><th>差价</th><th>建议</th></tr>
                                    <tr><td>SKU-A1001</td><td>¥100.00</td><td>¥95.00</td><td style="color:#dc3545;">-¥5</td><td><span class="mock-tag mock-tag-warning">⚡ 建议跟价</span></td></tr>
                                    <tr><td>SKU-B2003</td><td>¥85.00</td><td>¥85.00</td><td style="color:#28a745;">持平</td><td><span class="mock-tag mock-tag-success">✅ 正常</span></td></tr>
                                    <tr><td>SKU-C3005</td><td>¥120.00</td><td>¥115.00</td><td style="color:#dc3545;">-¥5</td><td><span class="mock-tag mock-tag-warning">⚡ 建议跟价</span></td></tr>
                                </table>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">🔒 保本线设置</div>
                                <div class="mock-panel">
                                    <div class="mock-row"><span class="mock-label">最低保本毛利率</span><span class="mock-value">15.0%</span></div>
                                    <div class="mock-row"><span class="mock-label">跟价策略</span><span class="mock-value">智能自动跟价</span></div>
                                    <div class="mock-row"><span class="mock-label">活动价保护</span><span class="mock-value">✅ 已开启</span></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>实时监控竞品降价</strong> — 自动追踪竞品价格，按你锁定的保本线自动跟价，不盲目内卷</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>竞品降价自动跟价，保本线由你锁定，守住每一分利润
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 7: 库存预警管理 ──────────
        elif current_step == 7:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">🚨 库存预警管理 — 安全库存与补货建议</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #dc3545; background: #fff5f5;">
                                <div class="mock-col-title" style="color: #dc3545; font-weight: 700;">🚨 预警SKU（2条）</div>
                                <div class="mock-highlight-red" style="margin-bottom:0.4rem;">
                                    <strong>🔴 SKU-A1001</strong> — 库存仅剩12件，低于安全库存50件，建议立即补货
                                </div>
                                <div class="mock-highlight" style="margin-bottom:0.4rem;">
                                    <strong>🟡 SKU-D4002</strong> — 月销仅5件，库存积压200件，建议清仓处理
                                </div>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">📊 库存分析</div>
                                <div class="mock-panel">
                                    <div class="mock-row"><span class="mock-label">总SKU数</span><span class="mock-value">42</span></div>
                                    <div class="mock-row"><span class="mock-label">库存健康</span><span class="mock-value" style="color:#28a745;">85%</span></div>
                                    <div class="mock-row"><span class="mock-label">预警SKU</span><span class="mock-value" style="color:#dc3545;">3</span></div>
                                    <div class="mock-row"><span class="mock-label">滞销SKU</span><span class="mock-value" style="color:#ffc107;">5</span></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>安全库存预警</strong> — 低于安全库存自动告警，断货前提醒，防止丢流量</div>
                    </div>
                    <div class="annotation">
                        <div class="annotation-arrow">②</div>
                        <div class="annotation-text"><strong>滞销SKU自动识别</strong> — 销量低迷的SKU自动标注并给出清仓建议，减少资金占用</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>防断货、防积压，资金和流量双保住
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 8: 活动自动报名 ──────────
        elif current_step == 8:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">🎯 平台活动管理 — 自动抓取与批量报名</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">🎉 可报名活动列表</div>
                                <table class="mock-table">
                                    <tr><th>活动名称</th><th>截止时间</th><th>匹配SKU</th><th>状态</th></tr>
                                    <tr><td>618年中大促</td><td>2026-06-01</td><td>12 个</td><td><span class="mock-tag mock-tag-success">可报名</span></td></tr>
                                    <tr><td>夏日清仓季</td><td>2026-05-25</td><td>8 个</td><td><span class="mock-tag mock-tag-success">可报名</span></td></tr>
                                    <tr><td>新品首发专场</td><td>2026-05-20</td><td>5 个</td><td><span class="mock-tag mock-tag-warning">即将截止</span></td></tr>
                                </table>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">✅ 批量报名操作</div>
                                <div class="mock-panel">
                                    <div class="mock-row"><span class="mock-label">已选SKU数量</span><span class="mock-value">25 个</span></div>
                                    <div class="mock-row"><span class="mock-label">匹配活动数</span><span class="mock-value">3 个</span></div>
                                    <div class="mock-row"><span class="mock-label">预估活动流量</span><span class="mock-value">+200%</span></div>
                                </div>
                                <div style="margin-top:0.5rem;text-align:center;">
                                    <span class="mock-btn mock-btn-primary" style="font-size:0.9rem;padding:0.5rem 2rem;">📋 一键批量报名</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>自动抓取平台可报名活动</strong> — 系统自动获取当前可报名活动，展示匹配SKU数量、截止时间</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>自动匹配符合条件的活动，一键批量报名，不再错过大促流量
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 9: 消息与售后管理 ──────────
        elif current_step == 9:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">💬 消息售后 — 消息中心与智能分类</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #dc3545; background: #fff5f5;">
                                <div class="mock-col-title" style="color: #dc3545; font-weight: 700;">🔔 重要通知（3条未读）</div>
                                <div class="mock-highlight-red" style="margin-bottom:0.4rem;">
                                    <strong>🚨 处罚警告</strong> — SKU-A1001 涉嫌描述不符，请在24h内处理
                                </div>
                                <div class="mock-highlight-red" style="margin-bottom:0.4rem;">
                                    <strong>📋 售后请求</strong> — 订单 #T12345 买家申请退货，待审核
                                </div>
                                <div class="mock-highlight-red">
                                    <strong>⏰ 核价超时提醒</strong> — 3条核价通知即将超时自动处理
                                </div>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">🏷️ 消息分类</div>
                                <div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:0.6rem;">
                                    <span class="mock-tag mock-tag-danger">处罚通知 3</span>
                                    <span class="mock-tag mock-tag-warning">售后请求 5</span>
                                    <span class="mock-tag mock-tag-info">核价通知 8</span>
                                    <span class="mock-tag mock-tag-success">系统通知 12</span>
                                </div>
                                <div style="margin-top:0.5rem;">
                                    <span class="mock-btn mock-btn-primary" style="font-size:0.78rem;">📋 一键处理待办</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>消息自动分类，重要消息置顶</strong> — 处罚、售后、核价等消息自动归类，紧急消息红色高亮，不遗漏</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>售后通知、处罚消息实时同步提醒，避免处罚漏看扣分罚款
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step 10: 数据大屏与报表 ──────────
        elif current_step == 10:
            st.markdown(f"""
            <div class="demo-carousel">
                <div class="demo-step-title"><span class="demo-step-badge">{current_step}</span>{_step_title}</div>
                <div class="mock-ui">
                    <div class="mock-ui-header">
                        <span><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>
                        <span style="margin-left: 0.5rem;">📈 多店铺大屏 + 数据报表 — 运营状态一览无余</span>
                    </div>
                    <div class="mock-ui-body">
                        <div class="mock-two-col">
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">📊 核心指标 <span style="float:right;font-size:0.75rem;color:#999;">今日实时</span></div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
                                    <div class="mock-panel" style="margin:0;text-align:center;">
                                        <div style="font-size:0.7rem;color:#999;">多店总销售额</div>
                                        <div style="font-size:1.1rem;font-weight:bold;color:#28a745;">¥45,280</div>
                                    </div>
                                    <div class="mock-panel" style="margin:0;text-align:center;">
                                        <div style="font-size:0.7rem;color:#999;">多店总利润</div>
                                        <div style="font-size:1.1rem;font-weight:bold;color:#667eea;">¥11,320</div>
                                    </div>
                                    <div class="mock-panel" style="margin:0;text-align:center;">
                                        <div style="font-size:0.7rem;color:#999;">整体利润率</div>
                                        <div style="font-size:1.1rem;font-weight:bold;color:#28a745;">25.0%</div>
                                    </div>
                                    <div class="mock-panel" style="margin:0;text-align:center;">
                                        <div style="font-size:0.7rem;color:#999;">待处理告警</div>
                                        <div style="font-size:1.1rem;font-weight:bold;color:#dc3545;">5 项</div>
                                    </div>
                                </div>
                            </div>
                            <div class="mock-col" style="border: 2px solid #667eea; background: #f8f9ff;">
                                <div class="mock-col-title" style="color: #667eea; font-weight: 700;">📋 报表管理</div>
                                <div class="mock-panel">
                                    <div class="mock-row"><span class="mock-label">📄 运营日报</span><span class="mock-value" style="font-size:0.75rem;">2026-05-14</span></div>
                                    <div class="mock-row"><span class="mock-label">📄 周度利润报告</span><span class="mock-value" style="font-size:0.75rem;">第19周</span></div>
                                    <div class="mock-row"><span class="mock-label">📄 库存分析报表</span><span class="mock-value" style="font-size:0.75rem;">实时</span></div>
                                    <div class="mock-row"><span class="mock-label">📄 活动效果复盘</span><span class="mock-value" style="font-size:0.75rem;">上月</span></div>
                                    <div class="mock-row"><span class="mock-label">📄 财务对账报表</span><span class="mock-value" style="font-size:0.75rem;">本期</span></div>
                                </div>
                                <div style="margin-top:0.5rem;text-align:center;">
                                    <span class="mock-btn mock-btn-success" style="font-size:0.85rem;">📥 一键导出报表</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="annotations-group">
                    <div class="annotation">
                        <div class="annotation-arrow">①</div>
                        <div class="annotation-text"><strong>多店统一总控</strong> — 一个后台管理所有店铺的盈亏/待办/告警，各店数据横向对比，不用来回切换后台</div>
                    </div>
                    <div class="annotation">
                        <div class="annotation-arrow">②</div>
                        <div class="annotation-text"><strong>每日自动生成报表</strong> — 运营日报、利润报告、库存分析、财务对账等报表每日自动生成，一键导出</div>
                    </div>
                </div>
                <div class="demo-footer-text">
                    💡 <strong>效果：</strong>一键掌握全店运营状态，不用手动做表看数据
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ────────── Step indicator (10 dots) ──────────
        _dots_html = '<div class="step-indicator">'
        for i in range(1, 11):
            if i == current_step:
                _dots_html += '<span class="step-dot active"></span>'
            else:
                _dots_html += '<span class="step-dot"></span>'
        _dots_html += '</div>'
        _dots_html += f'<div class="step-label active" style="text-align:center;">{current_step} / 10 · {_step_names[current_step-1]}</div>'
        st.markdown(_dots_html, unsafe_allow_html=True)

        # ────────── Navigation buttons ──────────
        col_p1, col_p2, col_p3, col_p4, col_p5, col_p6 = st.columns([1, 1, 0.5, 1, 1, 1.5])
        with col_p2:
            if current_step > 1:
                if st.button("◀ 上一步", use_container_width=True):
                    st.session_state["demo_step"] = current_step - 1
            else:
                st.markdown('<div style="height:37px;"></div>', unsafe_allow_html=True)
        with col_p4:
            if current_step < 10:
                if st.button("下一步 ▶", use_container_width=True, type="primary"):
                    st.session_state["demo_step"] = current_step + 1
            else:
                st.markdown('<div style="height:37px;"></div>', unsafe_allow_html=True)
        with col_p6:
            if st.button("✕ 关闭演示", use_container_width=True, type="secondary"):
                st.session_state["show_demo"] = False
                st.session_state.pop("demo_step", None)

        st.markdown('</div>', unsafe_allow_html=True)

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
        st.markdown("""<div class="stat-item"><div class="stat-number">高效</div><div class="stat-label">🤖 智能辅助运营管理</div></div>""", unsafe_allow_html=True)

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
    st.markdown("""<h2 id="solutions">🚀 全流程辅助，每个环节都帮你提效</h2>""", unsafe_allow_html=True)

    sol_rows = [
        [
            ("全自动核价", "智能核价提醒，避免遗漏，轻松管理",
             "手动核价30分钟，还漏处理导致商品下架",
             "按预设毛利规则批量自动处理核价通知，超时强提醒",
             "节省运营时间，降低遗漏风险"),
            ("库存智能管理", "防断货、防积压，资金和流量双保住",
             "断货丢流量，滞销压资金",
             "安全库存预警+销量预测+滞销SKU识别，自动生成补货建议",
             "智能库存管理，优化资金周转"),
        ],
        [
            ("智能自动调价", "跟价不亏，守住每一分利润",
             "跟价就亏，不跟价就没单",
             "竞品实时监控+保本毛利锁定+活动价定时切换",
             "保毛利前提下自动跟价，助力利润优化"),
            ("活动自动报名", "一键匹配，轻松参与活动",
             "手动找活动、筛选SKU，错过报名时间",
             "自动抓取可报活动+SKU匹配+批量报名+状态追踪",
             "及时获知活动信息，不错过报名机会"),
        ],
        [
            ("数据自动分析预警", "自动找问题，快速掌握店铺状态",
             "做报表1小时，还找不到问题",
             "每日自动生成报表，异常指标实时预警，给出优化建议",
             "批量处理，快速出结果"),
            ("消息与售后自动化", "集中管理，减少遗漏",
             "消息太多看不过来，处罚通知漏看",
             "消息智能分类+重要通知强提醒+售后模板一键复用",
             "集中管理通知，减少遗漏"),
        ],
        [
            ("标签与发货自动化", "批量处理发货流程，节省时间",
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
            <div class="value-tag">智能核价提醒，避免遗漏，轻松管理</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">📊 全自动核价模块</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 🔄 批量导入订单自动匹配核价规则<br>
                • 🤖 按预设毛利自动接受/拒绝核价通知<br>
                • ⏰ 超时未处理自动强提醒，不漏单<br>
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
                • 🔎 竞品价格实时监控，变动即时预警<br>
                • 🔒 保本毛利底线锁定，跟价不亏本<br>
                • 📅 活动价/日常价定时自动切换<br>
                • 📋 调价历史全记录，利润变化一目了然
            </p>
        </div>
        """, unsafe_allow_html=True)

    col_f4, col_f5, col_f6 = st.columns(3)

    with col_f4:
        st.markdown("""
        <div class="feature-card">
            <div class="value-tag">一键匹配，轻松参与活动</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">🎯 平台活动自动报名</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 🔍 自动抓取可报名活动，智能匹配店铺SKU<br>
                • 📋 一键批量报名，省去逐个筛选时间<br>
                • 📊 活动状态追踪，已报/待报一目了然<br>
                • ⏰ 报名截止前自动提醒，不错过任何大促
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_f5:
        st.markdown("""
        <div class="feature-card">
            <div class="value-tag">自动找问题，快速掌握店铺状态</div>
            <h3 style="color: #667eea; margin: 0.6rem 0 0.5rem 0; font-size: 1.05rem;">📈 数据自动分析与预警</h3>
            <p style="color: #555; line-height: 1.7; font-size: 0.93rem;">
                • 📋 每日自动生成运营日报，数据不遗漏<br>
                • 🚨 异常指标实时预警（利润/库存/风险等）<br>
                • 📊 趋势图表可视化，一眼看懂数据变化<br>
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
            <p style="font-size: 0.82rem; opacity: 0.85; margin-bottom: 0.5rem;">全流程辅助，轻松管理运营</p>
            <div class="price-amount">¥79.2<span style="font-size: 1.15rem;">/季度</span><br><span class="price-savings">省40%</span></div>
            <p style="font-size: 0.88rem; opacity: 0.9; margin: 0.4rem 0;">原价 ¥99/季度 | 限时8折</p>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 1.9; opacity: 0.95; margin: 1rem 0; font-size: 0.92rem;">
                ✅ 包含所有基础版功能<br>
                ✅ 智能辅助模块（核价/库存/调价/活动/消息）<br>
                ✅ 多店铺统一管理+高级数据分析<br>
                ✅ 优先客服支持+专属运营建议<br>
            </ul>
            <p style="font-size: 0.85rem; font-weight: bold; opacity: 0.9; margin-top: 0.5rem;">🔥 高效运营的必备方案</p>
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
        <h3 style="text-align: center; color: #333; margin-bottom: 1.2rem; font-size: 1.2rem;">💰 选择套餐，立即开通</h3>
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
            st.image("assets/WeChat_20260512015412.png", width=230, caption="微信扫码付款")
        except Exception as e:
            st.warning("⚠️ 微信收款码加载失败，请刷新页面或联系客服")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_qr2:
        st.markdown("""<div class="qr-code-container"><span class="qr-label" style="color: #1677FF;">💙 支付宝</span>""", unsafe_allow_html=True)
        try:
            st.image("assets/paypal_20260512015446.jpg", width=230, caption="支付宝扫码付款")
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
                感谢您选择 <strong>{order.get('plan', '跨境卖家运营辅助工具')}</strong>！<br>
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

    st.markdown("""<p style="text-align: center; color: #666; font-size: 0.92rem; margin-bottom: 1.2rem;">已助力 <strong style="color: #667eea;">众多</strong> 卖家提升运营效率</p>""", unsafe_allow_html=True)

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #555; line-height: 1.7; font-size: 0.95rem;">
                "以前每天运营要花<strong>3小时</strong>，现在每天看告警和管理数据，每月省了大量时间，<strong style="color: #28a745;">利润明显提升</strong>！"
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
                "一个后台管5家店，不用来回切换后台，<strong>运营效率明显提升</strong>，多店管理方便多了！<strong style="color: #667eea;">多店卖家必备</strong>"
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
            <h2 style="margin-bottom: 0.6rem; font-size: 1.6rem;">🚀 高效运营，轻松管理</h2>
            <p style="margin-bottom: 1.2rem; font-size: 0.95rem; opacity: 0.95; line-height: 1.6;">
                核价、库存、调价、活动、发货一站式管理<br>
                把时间花在选品和业务上，而不是盯后台做报表<br>
                <span style="font-size: 0.88rem;">✅ 免费试用 7 天 | ✅ 无需信用卡 | ✅ 随时可取消</span>
            </p>
            <div style="display: flex; gap: 0.6rem; justify-content: center; flex-wrap: wrap;">
                <a href="?page=app" class="cta-button-primary" style="color: white; text-decoration: none;">🚀 免费试用7天 →</a>
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
        <p style="margin: 0.3rem 0; font-size: 0.88rem;">© 2026 跨境卖家运营辅助工具 | 专注数据与运营管理 🤖</p>
        <p style="margin: 0.3rem 0; font-size: 0.8rem; color: #aaa;">本工具仅用于辅助商家进行数据分析和运营决策，不构成任何投资建议</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    show_landing_page()

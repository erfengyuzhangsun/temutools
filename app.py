import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime, date
from calculator import ProfitCalculator
from risk_monitor import RiskMonitor
from config import CATEGORY_COMMISSION_RATES, PRICING_PLANS, PROFIT_WARNING_THRESHOLD

from db import get_or_create_shop, save_profit_stats, save_sku_profits, save_risk_metrics
from auth import is_authenticated, get_current_user, get_user_id, get_user_info, logout, show_login_page
from admin import show_admin_panel, is_admin
from logger import log_action, log_error, logger

from modules.api_sync import ui as api_sync_ui
from modules.pricing import ui as pricing_ui
from modules.scheduler import ui as scheduler_ui
from modules.inventory import ui as inventory_ui
from modules.analysis import ui as analysis_ui
from modules.pricing_adj import ui as pricing_adj_ui
from modules.finance import ui as finance_ui
from modules.dashboard import ui as dashboard_ui
from modules.message import ui as message_ui
from modules.shipping import ui as shipping_ui
from modules.activity import ui as activity_ui
from modules.risk_inspection import ui as risk_inspection_ui
from modules.batch_ops import ui as batch_ops_ui
from modules.review_monitor import ui as review_monitor_ui
from modules.product_research import ui as product_research_ui
from modules.supplier import ui as supplier_ui
from modules.server_monitor import ui as server_monitor_ui


def save_analysis_to_db(user_id, summary, results_df, risk_report):
    try:
        shop_id = get_or_create_shop(user_id)
        save_profit_stats(user_id, shop_id, summary)
        sku_df = results_df.groupby(['SKU', '商品名称', '类目']).agg({
            '订单号': 'count', '买家支付': 'sum', '成本价': 'sum',
            '利润': 'sum', '总扣费': 'sum'
        }).reset_index()
        sku_df.columns = ['SKU', '商品名称', '类目', '订单数', '买家支付', '成本价', '利润', '总扣费']
        sku_df['利润率'] = (sku_df['利润'] / sku_df['成本价'].replace(0, 0.01) * 100).round(2)
        save_sku_profits(user_id, shop_id, sku_df)
        save_risk_metrics(user_id, shop_id, risk_report)
        log_action("分析结果已保存到数据库", user_id)
        return True
    except Exception as e:
        log_error(f"保存分析结果失败: {e}", user_id)
        return False


if 'db_initialized' not in st.session_state:
    try:
        from db_init import initialize_all_tables
        initialize_all_tables()
        st.session_state['db_initialized'] = True
        log_action("数据库初始化完成")
    except Exception as e:
        log_error(f"数据库初始化失败: {e}")

st.set_page_config(
    page_title="跨境卖家运营辅助工具",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    html {
        color-scheme: light !important;
    }
    html, body, .stApp, .main, .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stBottom"],
    [data-testid="stMainMenu"],
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stMarkdownContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="stElementContainer"],
    [data-testid="column"],
    [data-testid="stText"],
    [data-testid="stCaption"],
    [data-testid="stInfo"],
    [data-testid="stSuccess"],
    [data-testid="stWarning"],
    [data-testid="stError"],
    [data-testid="stException"],
    [data-testid="stMetric"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"],
    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    [data-testid="stForm"],
    [data-testid="stFormBorder"],
    [data-testid="stSelectbox"],
    [data-testid="stMultiselect"],
    [data-testid="stNumberInput"],
    [data-testid="stTextInput"],
    [data-testid="stTextArea"],
    [data-testid="stDateInput"],
    [data-testid="stTimeInput"],
    [data-testid="stSlider"],
    [data-testid="stCheckbox"],
    [data-testid="stRadio"],
    [data-testid="stToggle"],
    [data-testid="stColorPicker"],
    [data-testid="stFileUploader"],
    [data-testid="stImage"],
    [data-testid="stVideo"],
    [data-testid="stAudio"],
    [data-testid="stPlotlyChart"],
    [data-testid="stVegaLiteChart"],
    [data-testid="stDeckGlChart"],
    [data-testid="stGraphVizChart"],
    [data-testid="stBokehChart"],
    [data-testid="stPyplotChart"],
    [data-testid="stAltairChart"],
    [data-testid="stProgress"],
    [data-testid="stSpinner"],
    [data-testid="stBalloons"],
    [data-testid="stSnow"],
    [data-testid="stCode"],
    [data-testid="stJson"],
    [data-testid="stTabs"],
    [data-testid="stTab"],
    [data-testid="stExpander"],
    [data-testid="stExpanderToggle"],
    [data-testid="stPopover"],
    [data-testid="stModal"],
    [data-testid="stTooltip"],
    [data-testid="stHelp"],
    [data-testid="stAlert"],
    [data-testid="stBanner"],
    [data-testid="stNotification"],
    [data-testid="stToast"],
    [data-testid="stEmpty"],
    [data-testid="stHeading"],
    [data-testid="stSubheading"],
    [data-testid="stDivider"],
    [data-testid="stSeparator"],
    [data-testid="stLinkButton"],
    [data-testid="stDownloadButton"],
    [data-testid="stActionButton"],
    [data-testid="stPageLink"],
    [data-testid="stTabBar"],
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        background-color: #FFFFFF !important;
        color: #1E1E1E !important;
    }
    * {
        color: #1E1E1E !important;
        border-color: #DEE2E6 !important;
    }
    svg, [data-testid="stMetricValue"] svg,
    [data-testid="stMetricDelta"] svg,
    .st-emotion-cache * svg,
    .stMarkdown svg {
        fill: #1E1E1E !important;
        color: #1E1E1E !important;
        stroke: #1E1E1E !important;
    }
    a, a:link, a:visited, a:hover, a:active {
        color: #667EEA !important;
    }
    a.cta-button-primary, a.cta-button-primary:link,
    a.cta-button-primary:visited, a.cta-button-primary:hover {
        color: #FFFFFF !important;
    }
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-primaryFormSubmit"] {
        color: #FFFFFF !important;
    }
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-secondaryFormSubmit"] {
        color: #1E1E1E !important;
    }
    [data-testid="baseButton-tertiary"],
    [data-testid="baseButton-tertiaryFormSubmit"] {
        color: #1E1E1E !important;
    }
    button, [data-testid="baseButton-primary"] button,
    [data-testid="baseButton-secondary"] button,
    .stButton button {
        color: #1E1E1E !important;
    }
    button[kind="primary"] {
        color: #FFFFFF !important;
    }
    .stSidebar, [data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
    }
    .stSidebar *, [data-testid="stSidebar"] * {
        background-color: #F8F9FA !important;
        color: #1E1E1E !important;
    }
    .stSidebar .stButton button,
    [data-testid="stSidebar"] button {
        background-color: #F0F2F6 !important;
        color: #1E1E1E !important;
    }
    .stSidebar button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #FFFFFF !important;
    }
    input, textarea, select,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] select,
    .stTextInput input, .stTextArea textarea,
    .stNumberInput input, .stDateInput input,
    .stTimeInput input, .stSelectbox div,
    .stMultiselect div {
        background-color: #FFFFFF !important;
        color: #1E1E1E !important;
        border-color: #DEE2E6 !important;
    }
    .st-cc, .st-bb, .st-bc, .st-bd, .st-be, .st-bf,
    .st-bg, .st-bh, .st-bi, .st-bj, .st-bk, .st-bl,
    .st-bm, .st-bn, .st-bo, .st-bp, .st-bq, .st-br,
    .st-bs, .st-bt, .st-bu, .st-bv, .st-bw, .st-bx,
    .st-by, .st-bz, .st-ca, .st-cb, .st-cc, .st-cd,
    .st-ce, .st-cf, .st-cg, .st-ch, .st-ci, .st-cj,
    .st-ck, .st-cl, .st-cm, .st-cn, .st-co, .st-cp,
    .st-cq, .st-cr, .st-cs, .st-ct, .st-cu, .st-cv,
    .st-cw, .st-cx, .st-cy, .st-cz, .st-da, .st-db,
    .st-dc, .st-dd, .st-de, .st-df, .st-dg, .st-dh,
    .st-di, .st-dj, .st-dk, .st-dl, .st-dm, .st-dn,
    .st-do, .st-dp, .st-dq, .st-dr, .st-ds, .st-dt,
    .st-emotion-cache,
    .st-emotion-cache * {
        color: #1E1E1E !important;
    }
    [data-theme="dark"],
    [data-testid="stAppViewContainer"][data-theme="dark"],
    .stApp[data-theme="dark"] {
        background-color: #FFFFFF !important;
        color: #1E1E1E !important;
    }
    [data-theme="dark"] .stSidebar,
    [data-theme="dark"] [data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
    }
    [data-theme="dark"] input,
    [data-theme="dark"] textarea,
    [data-theme="dark"] select {
        background-color: #FFFFFF !important;
        color: #1E1E1E !important;
    }
</style>
""", unsafe_allow_html=True)

_query_params = st.query_params
_raw_page = _query_params.get("page", ["landing"])
_query_page = _raw_page[0] if isinstance(_raw_page, (list, tuple)) else _raw_page
_has_page_param = "page" in _query_params

if "page" not in st.session_state:
    st.session_state["page"] = _query_page
elif _has_page_param and _query_page != st.session_state["page"]:
    st.session_state["page"] = _query_page

if st.session_state.get('_rerun_pending', False):
    st.session_state['_rerun_pending'] = False

current_page = st.session_state["page"]

try:
    if current_page == "landing":
        import landing
        landing.show_landing_page()
        st.stop()

    if not is_authenticated():
        show_login_page()
        st.stop()
except Exception:
    st.error("页面加载中，请稍候...")
    st.stop()

MODULE_PAGES = {
    "api_sync": api_sync_ui.show_page,
    "pricing": pricing_ui.show_page,
    "scheduler": scheduler_ui.show_page,
    "inventory": inventory_ui.show_page,
    "analysis": analysis_ui.show_page,
    "pricing_adj": pricing_adj_ui.show_page,
    "finance": finance_ui.show_page,
    "dashboard": dashboard_ui.show_page,
    "message": message_ui.show_page,
    "shipping": shipping_ui.show_page,
    "activity": activity_ui.show_page,
    "risk_inspection": risk_inspection_ui.show_page,
    "batch_ops": batch_ops_ui.show_page,
    "review_monitor": review_monitor_ui.show_page,
    "product_research": product_research_ui.show_page,
    "supplier": supplier_ui.show_page,
    "server_monitor": server_monitor_ui.render_server_monitor,
}

if 'calculator' not in st.session_state:
    st.session_state['calculator'] = ProfitCalculator()

if 'results_df' not in st.session_state:
    st.session_state['results_df'] = None

if 'summary' not in st.session_state:
    st.session_state['summary'] = None

if 'risk_report' not in st.session_state:
    st.session_state['risk_report'] = None

if 'first_visit' not in st.session_state:
    st.session_state['first_visit'] = True

if st.session_state.get('_needs_rerun', False):
    st.session_state['_needs_rerun'] = False
    if not st.session_state.get('_rerun_pending', False):
        st.session_state['_rerun_pending'] = True
        st.rerun()
    st.stop()

with st.sidebar:
    user_info = get_user_info()
    if user_info:
        plan_names = {'basic': '基础版', 'pro': '专业版', 'lifetime': '终身版'}
        plan_display = plan_names.get(user_info.get('plan_type', ''), user_info.get('plan_type', ''))
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                    padding: 0.8rem; border-radius: 10px; margin-bottom: 1rem;
                    border: 1px solid #667eea30;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
                <span style="font-size: 1.2rem;">👤</span>
                <span style="font-weight: bold; color: #333; font-size: 0.9rem;">{user_info.get('wechat_nickname', '用户')}</span>
            </div>
            <div style="font-size: 0.8rem; color: #667eea; font-weight: 500;">
                {plan_display}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧭 功能导航")

    def nav_button(label, page, page_icon):
        current = st.session_state.get("page", "app")
        is_active = current == page
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{page_icon} {label}", key=f"nav_{page}", use_container_width=True, type=btn_type):
            st.session_state["page"] = page
            st.query_params["page"] = page
            if not st.session_state.get('_rerun_pending', False):
                st.session_state['_rerun_pending'] = True
                st.rerun()

    with st.expander("📊 核心工具", expanded=True):
        nav_button("利润分析", "app", "💰")
        nav_button("多店铺大屏", "dashboard", "📊")
        nav_button("API数据同步", "api_sync", "🔄")
        nav_button("核价自动化", "pricing", "💵")
        nav_button("定时任务", "scheduler", "⏰")

    with st.expander("📦 运营管理", expanded=False):
        nav_button("库存管理", "inventory", "📦")
        nav_button("数据分析", "analysis", "📈")
        nav_button("智能调价", "pricing_adj", "🏷️")
        nav_button("财务对账", "finance", "💳")
        nav_button("标签发货", "shipping", "📋")

    with st.expander("🛡️ 风控 & 自动化", expanded=False):
        nav_button("消息售后", "message", "💬")
        nav_button("活动报名", "activity", "🎯")
        nav_button("风控体检", "risk_inspection", "🔍")
        nav_button("批量运营", "batch_ops", "📋")
        nav_button("差评监控", "review_monitor", "⭐")
        nav_button("云主机监控", "server_monitor", "🖥️")
        nav_button("选品辅助", "product_research", "🔬")
        nav_button("供应商管理", "supplier", "🏭")

    st.markdown("---")
    st.header("📂 数据导入")
    
    uploaded_file = st.file_uploader(
        "上传 Temu 订单 CSV 文件",
        type=['csv'],
        help="支持从 Temu 商家后台导出的订单数据"
    )
    
    if uploaded_file:
        try:
            stringio = StringIO(uploaded_file.getvalue().decode('utf-8'))
            df = pd.read_csv(stringio)
            
            st.success(f"✅ 成功读取 **{len(df)}** 条订单数据")
            st.dataframe(df.head(3), width='stretch')
            
            if st.button("🚀 开始分析", width='stretch', type="primary"):
                with st.spinner("🔄 正在计算利润并分析风险..."):
                    calculator = ProfitCalculator()
                    results_df, summary = calculator.process_csv(df)
                    
                    monitor = RiskMonitor()
                    monitor.calculate_risk_from_csv(df)
                    risk_report = monitor.generate_risk_report()
                    
                    st.session_state['results_df'] = results_df
                    st.session_state['summary'] = summary
                    st.session_state['calculator'] = calculator
                    st.session_state['original_df'] = df
                    st.session_state['risk_report'] = risk_report
                    st.session_state['monitor'] = monitor

                    user_id = get_user_id()
                    if user_id:
                        save_analysis_to_db(user_id, summary, results_df, risk_report)

                    if not st.session_state.get('_rerun_pending', False):
                        st.session_state['_rerun_pending'] = True
                        st.rerun()
                    
        except Exception as e:
            st.error(f"❌ 文件处理失败：{str(e)}")
    
    st.markdown("---")
    
    st.header("⚙️ 快速测试")
    
    if st.button("📊 使用示例数据", width='stretch'):
        sample_data = {
            '订单号': [f'ORD202605{i:03d}' for i in range(1, 21)],
            'SKU': ['SKU_BL001', 'SKU_3C001', 'SKU_CZ001', 'SKU_MZ001', 'SKU_WJ001',
                   'SKU_BL002', 'SKU_3C002', 'SKU_CZ002', 'SKU_SP001', 'SKU_WJ002',
                   'SKU_BL003', 'SKU_3C003', 'SKU_MZ002', 'SKU_CZ003', 'SKU_WJ003',
                   'SKU_BL004', 'SKU_3C004', 'SKU_CZ004', 'SKU_MZ003', 'SKU_SP002'],
            '商品名称': [
                '北欧风简约收纳盒套装', '无线蓝牙耳机Pro版', '夏季轻薄透气运动T恤',
                '玻尿酸保湿精华液30ml', '儿童益智积木玩具100片', '多功能厨房置物架',
                '智能手表运动版', '韩版宽松休闲卫衣', '有机坚果礼盒500g', '婴儿早教布书套装',
                'ins风桌面收纳架', 'Type-C快充数据线3条装', '烟酰胺美白面膜10片',
                '复古高腰牛仔裤女', '乐高式拼装汽车模型', '不锈钢厨房锅铲套装五件套',
                '便携式蓝牙音箱迷你小音响', '冰丝防晒衣女夏季防紫外线外套',
                '氨基酸洗面奶温和清洁控油两支装', '进口零食大礼包混合装500g'
            ],
            '买家支付金额': [68.5, 159.0, 89.9, 45.8, 125.0, 52.0, 299.0, 78.0, 98.0, 168.0,
                          35.9, 29.9, 88.0, 129.0, 189.0, 46.8, 79.0, 65.9, 56.0, 78.9],
            '平台运费': [8.0, 12.0, 6.0, 5.0, 10.0, 6.0, 15.0, 5.0, 7.0, 12.0,
                       5.0, 3.0, 5.0, 6.0, 10.0, 5.0, 6.0, 5.0, 4.0, 6.0],
            '结算价': [32.0, 85.0, 42.0, 22.0, 58.0, 28.0, 155.0, 38.0, 48.0, 92.0,
                     18.0, 15.0, 42.0, 62.0, 98.0, 24.0, 42.0, 32.0, 28.0, 38.0],
            '类目': ['家居百货', '3C数码', '服装鞋包', '美妆个护', '玩具母婴',
                   '家居百货', '3C数码', '服装鞋包', '食品饮料', '玩具母婴',
                   '家居百货', '3C数码', '服装鞋包', '美妆个护', '玩具母婴',
                   '家居百货', '3C数码', '服装鞋包', '美妆个护', '食品饮料'],
            '发货时间': ['2026-05-01 10:30:00', '2026-05-02 09:15:00', '2026-05-02 11:40:00',
                        '2026-05-03 08:20:00', '2026-05-03 14:50:00', '2026-05-04 09:00:00',
                        '2026-05-04 16:30:00', '2026-05-05 10:10:00', '2026-05-05 13:45:00',
                        '2026-05-06 08:30:00', '2026-05-06 11:20:00', '2026-05-07 09:45:00',
                        '2026-05-07 15:10:00', '2026-05-08 10:00:00', '2026-05-08 14:25:00',
                        '2026-05-09 08:50:00', '2026-05-09 11:30:00', '2026-05-10 09:15:00',
                        '2026-05-10 13:40:00', '2026-05-11 08:20:00'],
            '确认收货时间': ['2026-05-15 14:20:00', '2026-05-09 16:45:00', '2026-05-09 10:30:00',
                            '2026-05-10 13:15:00', '2026-05-10 17:30:00', '2026-05-11 11:20:00',
                            '2026-05-11 15:40:00', '2026-05-12 09:25:00', '2026-05-12 16:50:00',
                            '2026-05-13 12:10:00', '2026-05-13 14:35:00', '2026-05-14 10:55:00',
                            '2026-05-14 16:40:00', '2026-05-15 11:30:00', '2026-05-15 15:50:00',
                            '2026-05-16 13:20:00', '2026-05-16 14:45:00', '2026-05-17 10:30:00',
                            '2026-05-17 15:55:00', '2026-05-18 12:10:00'],
            '退货状态': ['否', '否', '是', '否', '否', '否', '否', '是', '否', '否',
                        '否', '否', '否', '否', '否', '否', '否', '否', '否', '否'],
            '成本价': [25.0, 72.0, 35.0, 18.0, 48.0, 22.0, 138.0, 30.0, 40.0, 75.0,
                     14.0, 12.0, 35.0, 52.0, 82.0, 19.0, 34.0, 26.0, 22.0, 32.0],
            '店铺评分': [4.8, 4.9, 4.6, 4.8, 4.5, 4.3, 4.9, 4.4, 4.8, 4.7,
                       4.6, 4.9, 4.7, 4.3, 4.6, 4.5, 4.8, 4.5, 4.7, 4.8]
        }
        
        df = pd.DataFrame(sample_data)
        
        with st.spinner("🔄 正在生成示例数据并分析..."):
            calculator = ProfitCalculator()
            results_df, summary = calculator.process_csv(df)
            
            monitor = RiskMonitor()
            monitor.calculate_risk_from_csv(df)
            risk_report = monitor.generate_risk_report()
            
            st.session_state['results_df'] = results_df
            st.session_state['summary'] = summary
            st.session_state['calculator'] = calculator
            st.session_state['risk_report'] = risk_report
            st.session_state['monitor'] = monitor

            user_id = get_user_id()
            if user_id:
                save_analysis_to_db(user_id, summary, results_df, risk_report)

            if not st.session_state.get('_rerun_pending', False):
                st.session_state['_rerun_pending'] = True
                st.rerun()
    
    st.markdown("---")
    with st.expander("📌 使用说明（点击展开）", expanded=False):
        st.info("""
        1️⃣ 从 Temu 商家后台导出订单 CSV  
        2️⃣ 上传文件并点击"开始分析"  
        3️⃣ 查看风险仪表盘 + 利润报告  
        4️⃣ 导出报表进行进一步分析
        """)

    st.markdown("---")
    with st.expander("⚙️ 管理", expanded=False):
        if st.button("🔐 管理员控制台", use_container_width=True):
            st.session_state['show_admin'] = not st.session_state.get('show_admin', False)
        if st.button("🚪 退出登录", use_container_width=True, type="secondary"):
            logout()
            if not st.session_state.get('_rerun_pending', False):
                st.session_state['_rerun_pending'] = True
                st.rerun()

if current_page in MODULE_PAGES:
    MODULE_PAGES[current_page]()
    st.stop()

st.markdown("""
<style>
    .nav-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-brand {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        text-decoration: none;
    }
    
    .nav-links a {
        color: white;
        text-decoration: none;
        margin-left: 1.5rem;
        opacity: 0.9;
        transition: opacity 0.3s;
    }
    
    .nav-links a:hover {
        opacity: 1;
    }
</style>

<div class="nav-bar">
    <a href="?page=app" class="nav-brand">🤖 跨境卖家运营辅助工具</a>
    <div class="nav-links">
        <a href="?page=app">📊 分析工具</a>
        <a href="?page=landing">🏠 返回首页</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .risk-card-safe {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 5px solid #28a745;
        margin: 0.3rem 0;
        transition: transform 0.2s;
    }
    
    .risk-card-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 5px solid #ffc107;
        margin: 0.3rem 0;
        transition: transform 0.2s;
    }
    
    .risk-card-danger {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 5px solid #dc3545;
        margin: 0.3rem 0;
        transition: transform 0.2s;
        animation: pulse 2s infinite;
    }
    
    .risk-card-critical {
        background: linear-gradient(135deg, #e2e3e5 0%, #d3d4d5 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 5px solid #6c757d;
        margin: 0.3rem 0;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .health-score-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0 auto;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    
    .warning-banner {
        background: linear-gradient(90deg, #ff6b6b 0%, #ffa502 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🤖 跨境卖家运营辅助工具</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">全流程自动化运营 | 核价·库存·调价·活动·发货·售后一站式管理</p>', unsafe_allow_html=True)

if st.session_state['first_visit'] and st.session_state['results_df'] is None:
    with st.expander("👋 欢迎使用跨境卖家运营辅助工具！点击查看使用指南", expanded=True):
        col_guide1, col_guide2, col_guide3 = st.columns(3)
        
        with col_guide1:
            st.markdown("""
            <div style="background: #e7f3ff; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #007bff;">
                <h4>📂 第一步：导入数据</h4>
                <ol style="font-size: 0.9rem; line-height: 1.8;">
                    <li>从 Temu 商家后台导出订单 CSV</li>
                    <li>点击左侧"上传文件"按钮</li>
                    <li>或点击"使用示例数据"体验</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col_guide2:
            st.markdown("""
            <div style="background: #fff3cd; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ffc107;">
                <h4>⚙️ 第二步：开始分析</h4>
                <ol style="font-size: 0.9rem; line-height: 1.8;">
                    <li>上传文件后点击"开始分析"</li>
                    <li>等待 10-30 秒完成计算</li>
                    <li>查看风险仪表盘和利润报告</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col_guide3:
            st.markdown("""
            <div style="background: #d4edda; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #28a745;">
                <h4>📊 第三步：查看报告</h4>
                <ol style="font-size: 0.9rem; line-height: 1.8;">
                    <li>顶部查看店铺健康评分</li>
                    <li>切换 Tab 查看详细报表</li>
                    <li>导出 Excel/CSV 进行分析</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("✅ 我知道了，开始使用", width='stretch'):
            st.session_state['first_visit'] = False
            st.session_state['_needs_rerun'] = True
    
    st.markdown("---")

if st.session_state.get('show_admin', False):
    show_admin_panel()
    st.stop()

if st.session_state['results_df'] is not None and st.session_state['summary'] is not None:
    results_df = st.session_state['results_df']
    summary = st.session_state['summary']
    calculator = st.session_state['calculator']
    risk_report = st.session_state.get('risk_report')
    
    if risk_report:
        health_score = risk_report['健康评分']
        grade = risk_report['等级']
        grade_label = risk_report['等级标签']
        grade_color = risk_report['等级颜色']
        
        danger_count = risk_report['指标统计']['危险']
        critical_count = risk_report['指标统计']['极危']
        warning_count = risk_report['指标统计']['关注']
        
        if critical_count > 0 or danger_count > 0:
            st.markdown(f"""
            <div class="warning-banner">
                🚨 店铺风险预警：{critical_count} 项极危 + {danger_count} 项危险指标！预计月罚款 ¥{risk_report['预计月罚款']:,.0f}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 店铺健康仪表盘")
        
        col_health, col_indicators = st.columns([1, 3])
        
        with col_health:
            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div class="health-score-circle" style="background: linear-gradient(135deg, {grade_color}20 0%, {grade_color}40 100%); color: {grade_color};">
                    <div>
                        <div style="font-size: 3rem; font-weight: bold;">{grade}</div>
                        <div style="font-size: 0.9rem; color: {grade_color};">{grade_label}</div>
                    </div>
                </div>
                <div style="margin-top: 1rem;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: {grade_color};">{health_score:.1f}/100</div>
                    <div style="color: #666;">综合健康评分</div>
                </div>
                <div style="margin-top: 1rem; background: white; padding: 0.8rem; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <small>🟢 安全 {risk_report['指标统计']['安全']}项</small><br>
                    <small>🟡 关注 {warning_count}项</small><br>
                    <small>🔴 危险 {danger_count}项</small><br>
                    <small>💀 极危 {critical_count}项</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_indicators:
            indicators_cols = st.columns(3)
            
            for idx, indicator in enumerate(risk_report['详细指标']):
                col = indicators_cols[idx % 3]
                
                status = indicator['状态'].split()[0] if ' ' in indicator['状态'] else indicator['状态'][0]
                
                card_class = f"risk-card-{indicator['状态'].split()[1].lower()}" if len(indicator['状态'].split()) > 1 else "risk-card-safe"
                
                with col:
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong>{indicator['指标名称']}</strong>
                            <span style="font-size: 1.3rem;">{status}</span>
                        </div>
                        <div style="font-size: 1.5rem; font-weight: bold; margin: 0.3rem 0;">
                            {indicator['当前值']}
                        </div>
                        <div style="font-size: 0.85rem; color: #666;">
                            安全区: {indicator['安全阈值']} | 预警线: {indicator['预警阈值']}
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; font-weight: 500;">
                            ⚡ {indicator['紧急程度']} · {indicator['可能处罚']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"### 📋 风险评估总结 ({risk_report['生成时间']})")
        st.info(risk_report['总结'])
        
        if risk_report['改进建议']:
            st.markdown("#### 🎯 优先改进建议")
            for suggestion in risk_report['改进建议'][:3]:
                priority_emoji = "🔥" if suggestion['priority'] == '高' else "⚠️"
                st.markdown(f"""
                <div style="background: {'#fff3cd' if suggestion['priority'] == '中' else '#f8d7da'}; 
                            padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; 
                            border-left: 4px solid {'#ffc107' if suggestion['priority'] == '中' else '#dc3545'};">
                    <strong>{priority_emoji} {suggestion['indicator']}</strong> 
                    ({suggestion['current_value']} → 目标 {suggestion['target_value']})<br>
                    <small>📅 截止时间：{suggestion['deadline']} | 💡 {suggestion['action'][:80]}...</small>
                </div>
                """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 利润总览", "📋 明细报表", "📈 SKU 分析", "⚠️ 风险详情"])
    
    with tab1:
        col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
        
        with col_metrics1:
            st.metric(label="总订单数", value=f"{summary['total_orders']} 单", delta=None)
        
        with col_metrics2:
            profit_color = "normal" if summary['total_profit'] >= 0 else "inverse"
            st.metric(
                label="总利润",
                value=f"¥{summary['total_profit']:,.2f}",
                delta=f"{summary['avg_profit_rate']:.1f}%",
                delta_color=profit_color
            )
        
        with col_metrics3:
            st.metric(
                label="总扣费",
                value=f"¥{summary['total_deduction']:,.2f}",
                delta=f"占收入 {summary['deduction_rate']:.1f}%"
            )
        
        with col_metrics4:
            st.metric(label="净利润率", value=f"{summary['net_margin']:.1f}%")
        
        st.markdown("---")
        
        col_warning, col_loss = st.columns(2)
        
        with col_warning:
            if summary['warning_orders'] > 0:
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: #ffc107;">
                    <h4>⚠️ 利润预警订单</h4>
                    <p style="font-size: 1.5rem; font-weight: bold; color: #ffc107;">
                        {summary['warning_orders']} 单（利润率 < {PROFIT_WARNING_THRESHOLD}%）
                    </p>
                    <p>这些订单需要立即关注，建议调整价格或下架商品！</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #d4edda; padding: 1rem; border-radius: 10px; border-left: 4px solid #28a745;">
                    <h4>✅ 状态良好</h4>
                    <p>所有订单利润率均在安全范围内</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col_loss:
            if summary['loss_orders'] > 0:
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: #dc3545;">
                    <h4>🔴 亏损订单</h4>
                    <p style="font-size: 1.5rem; font-weight: bold; color: #dc3545;">
                        {summary['loss_orders']} 单处于亏损状态
                    </p>
                    <p>这些订单每单都在亏钱！请立即检查定价策略！</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #d4edda; padding: 1rem; border-radius: 10px; border-left: 4px solid #28a745;">
                    <h4>✅ 无亏损订单</h4>
                    <p>所有订单均为盈利状态</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("💰 费用构成分析")
        
        fee_breakdown = results_df[['基础佣金', '支付处理费', '绩效附加费', '退货损耗', '运费罚款']].sum()
        
        col_fee = st.columns(5)
        fees = ['基础佣金', '支付处理费', '绩效附加费', '退货损耗', '运费罚款']
        for idx, (fee_name, col) in enumerate(zip(fees, col_fee)):
            amount = fee_breakdown[fee_name]
            percentage = (amount / summary['total_revenue']) * 100 if summary['total_revenue'] > 0 else 0
            
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <h6>{fee_name}</h6>
                    <p style="font-size: 1.3rem; font-weight: bold;">¥{amount:,.2f}</p>
                    <small>{percentage:.1f}%</small>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📋 订单明细报表")
        
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            sku_list = ['全部'] + list(results_df['SKU'].unique())
            selected_sku = st.selectbox("筛选 SKU", sku_list)
        
        with col_filter2:
            category_list = ['全部'] + list(results_df['类目'].unique())
            selected_category = st.selectbox("筛选类目", category_list)
        
        with col_filter3:
            status_options = ['全部', '预警', '正常']
            selected_status = st.selectbox("筛选状态", status_options)
        
        filters = {
            'sku': selected_sku,
            'category': selected_category,
            'status': selected_status
        }
        
        filtered_df = calculator.filter_data(results_df, filters)
        
        if not filtered_df.empty:
            st.success(f"显示 {len(filtered_df)} 条记录")
            
            def highlight_warning(val):
                if '🔴' in str(val):
                    return 'background-color: #ffcccc'
                return ''
            
            display_columns = ['订单号', 'SKU', '商品名称', '类目', '买家支付', '平台运费',
                             '基础佣金', '支付处理费', '绩效附加费', '退货损耗', '运费罚款',
                             '总扣费', '实际到账', '利润', '利润率%', '是否预警']
            
            styled_df = filtered_df[display_columns].style.map(highlight_warning, subset=['是否预警'])
            
            st.dataframe(styled_df, width='stretch', height=400)
            
            csv_filtered = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 导出筛选后的报表 (CSV)",
                data=csv_filtered,
                file_name='temu_profit_report_filtered.csv',
                mime='text/csv'
            )
        else:
            st.info("没有符合条件的数据")
    
    with tab3:
        st.subheader("📈 SKU 维度分析")
        
        sku_summary = calculator.get_sku_summary(results_df)
        
        if not sku_summary.empty:
            col_sku_table, col_sku_chart = st.columns([2, 1])
            
            with col_sku_table:
                def highlight_sku_status(val):
                    if '🔴' in str(val):
                        return 'background-color: #ffcccc; font-weight: bold'
                    elif '⚠️' in str(val):
                        return 'background-color: #fff3cd'
                    return ''
                
                styled_sku = sku_summary.style.map(highlight_sku_status, subset=['状态'])
                st.dataframe(styled_sku, width='stretch')
                
                csv_sku = sku_summary.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 导出 SKU 汇总表 (CSV)",
                    data=csv_sku,
                    file_name='temu_sku_summary.csv',
                    mime='text/csv'
                )
            
            with col_sku_chart:
                st.markdown("#### 🏆 TOP 5 盈利 SKU")
                top5_profit = sku_summary.head(5)[['商品名称', '总利润', '利润率']]
                st.dataframe(top5_profit, width='stretch')
                
                st.markdown("#### ⚠️ 需关注的 SKU")
                warning_skus = sku_summary[sku_summary['状态'].str.contains('🔴|⚠️')][['商品名称', '利润率', '状态']]
                if not warning_skus.empty:
                    st.dataframe(warning_skus, width='stretch')
                else:
                    st.success("✅ 所有 SKU 状态良好")
        
        st.markdown("---")
        
        st.subheader("📊 类目维度分析")
        
        cat_summary = calculator.get_category_summary(results_df)
        
        if not cat_summary.empty:
            col_cat_table, col_cat_chart = st.columns([2, 1])
            
            with col_cat_table:
                st.dataframe(cat_summary, width='stretch')
            
            with col_cat_chart:
                st.bar_chart(cat_summary.set_index('类目')['总利润'])
    
    with tab4:
        if risk_report:
            st.header("⚠️ 详细风险分析与罚款预测")
            
            st.subheader(f"📊 综合评级：{grade} 级 ({grade_label}) - {health_score:.1f}/100 分")
            
            col_risk_detail, col_penalty = st.columns([2, 1])
            
            with col_risk_detail:
                st.markdown("#### 📋 6 项核心风险指标")
                
                risk_df = pd.DataFrame(risk_report['详细指标'])
                
                def highlight_risk_status(row):
                    status = row['状态']
                    if '💀' in status:
                        return [''] * len(row)
                    elif '🔴' in status:
                        return ['background-color: #f8d7da; color: #721c24; font-weight: bold'] * len(row)
                    elif '🟡' in status:
                        return ['background-color: #fff3cd; color: #856404'] * len(row)
                    elif '🟢' in status:
                        return ['background-color: #d4edda; color: #155724'] * len(row)
                    return [''] * len(row)
                
                display_risk_df = risk_df[['指标名称', '当前值', '安全阈值', '危险阈值', '状态', '紧急程度', '可能处罚']]
                st.dataframe(display_risk_df, width='stretch')
            
            with col_penalty:
                st.markdown("#### 💸 月度罚款风险预测")
                
                penalties = risk_report['罚款明细']
                
                if penalties:
                    total_penalty = sum(p['amount'] for p in penalties.values())
                    
                    for penalty_name, penalty_info in penalties.items():
                        severity_emoji = "💀" if penalty_info['severity'] == "critical" else "🔴"
                        st.metric(
                            label=f"{severity_emoji} {penalty_name}",
                            value=f"¥{penalty_info['amount']:,.2f}",
                            delta=penalty_info['reason'],
                            delta_color="inverse"
                        )
                    
                    st.markdown(f"""
                    <div style="background-color: #f8d7da; padding: 1rem; border-radius: 10px; margin-top: 1rem; text-align: center;">
                        <strong>⚠️ 预计月罚款总额：¥{total_penalty:,.2f}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("✅ 当前各项指标正常，无预计罚款")
            
            st.markdown("---")
            
            if risk_report['预警记录']:
                st.subheader("🚨 最新预警记录")
                
                alerts_df = pd.DataFrame(risk_report['预警记录'])
                st.dataframe(alerts_df, width='stretch')
            
            st.markdown("---")
            
            st.subheader("📄 完整风险评估报告")
            
            with st.expander("查看/导出完整报告", expanded=False):
                report_text = f"""
=====================================
Temu 店铺风险评估报告
=====================================

生成时间：{risk_report['生成时间']}
店铺等级：{grade} 级 ({grade_label})
健康评分：{health_score:.1f}/100

【指标统计】
- 总指标数：{risk_report['指标统计']['总指标数']}
- ✅ 安全：{risk_report['指标统计']['安全']} 项
- ⚠️ 关注：{risk_report['指标统计']['关注']} 项
- 🔴 危险：{risk_report['指标统计']['危险']} 项
- 💀 极危：{risk_report['指标统计']['极危']} 项

【预计月罚款】¥{risk_report['预计月罚款']:,.2f}

【详细指标】
"""
                for indicator in risk_report['详细指标']:
                    report_text += f"""
{indicator['指标名称']}：
  当前值：{indicator['当前值']}
  状态：{indicator['状态']}
  紧急程度：{indicator['紧急程度']}
  可能处罚：{indicator['可能处罚']}
  建议：{indicator['建议']}

"""
                
                report_text += f"""
【总结】
{risk_report['总结']}

=====================================
报告生成完成
=====================================
"""
                
                st.text_area("", value=report_text, height=400)
                
                st.download_button(
                    label="📥 导出风险评估报告 (TXT)",
                    data=report_text.encode('utf-8'),
                    file_name=f'temu_risk_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                    mime='text/plain'
                )
    
    st.markdown("---")
    
    col_export1, col_export2, col_export3, col_export4 = st.columns(4)
    
    with col_export1:
        csv_full = results_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 导出 CSV",
            data=csv_full,
            file_name='temu_profit_report.csv',
            mime='text/csv',
            width='stretch'
        )
    
    with col_export2:
        try:
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                results_df.to_excel(writer, sheet_name='利润明细', index=False)
                
                summary_df = pd.DataFrame([summary])
                summary_df.to_excel(writer, sheet_name='汇总数据', index=False)
                
                if risk_report:
                    indicators_df = pd.DataFrame(risk_report['详细指标'])
                    indicators_df.to_excel(writer, sheet_name='风险指标', index=False)
            
            output.seek(0)
            
            st.download_button(
                label="📊 导出 Excel",
                data=output,
                file_name=f'temu_report_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                width='stretch'
            )
        except Exception as e:
            st.error(f"Excel导出失败：{str(e)}")
    
    with col_export3:
        st.markdown(f"""
        <div style="padding: 1rem; background-color: #e7f3ff; border-radius: 10px; text-align: center;">
            <h4>📈 数据概览</h4>
            <p style="margin: 0;"><strong>{summary['total_orders']}</strong> 单</p>
            <p style="margin: 0;">收入 ¥<strong>{summary['total_revenue']:,.0f}</strong></p>
            <p style="margin: 0;">利润 ¥<strong>{summary['total_profit']:,.0f}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_export4:
        if st.button("🔄 重新分析", width='stretch'):
            for key in ['results_df', 'summary', 'calculator', 'risk_report', 'monitor']:
                if key in st.session_state:
                    del st.session_state[key]
            if not st.session_state.get('_rerun_pending', False):
                st.session_state['_rerun_pending'] = True
                st.rerun()
    
    st.markdown("---")
    
    col_tip1, col_tip2, col_tip3 = st.columns(3)
    
    with col_tip1:
        st.info("""
        💡 **使用提示**
        
        - 数据仅在本地处理，不会上传
        - 建议每周分析一次订单数据
        - 关注利润率低于5%的SKU
        """)
    
    with col_tip2:
        st.success("""
        ✅ **功能特性**
        
        - 10+项费用精确拆分
        - 6大风险指标实时监控
        - SKU级深度利润分析
        - 一键导出完整报表
        """)
    
    with col_tip3:
        st.markdown("""
        📞 **需要帮助？**
        
        微信客服：`returnHuangMuNing`
        
        邮箱：`484478363@qq.com`
        
        工作时间：9:00-21:00
        """)

else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem;">
        <h2>👋 欢迎使用跨境卖家运营辅助工具</h2>
        <p style="font-size: 1.2rem; color: #666; margin: 2rem 0;">
            上传您的 Temu 订单 CSV 文件，即刻获取精确到分的利润分析和全流程自动化运营支持
        </p>
        <div style="background-color: #f8f9fa; padding: 2rem; border-radius: 15px; max-width: 900px; margin: 2rem auto;">
            <h3>✨ 核心功能亮点</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem; text-align: left;">
                <div>
                    <h4>🤖 全流程自动化</h4>
                    <ul style="font-size: 1rem; line-height: 1.8; color: #555;">
                        <li>✅ 自动核价处理，不漏单、不亏损</li>
                        <li>✅ 库存智能预警，防断货、防积压</li>
                        <li>✅ 智能自动调价，跟价不亏本</li>
                        <li>✅ 活动自动报名，不错过大促流量</li>
                    </ul>
                </div>
                <div>
                    <h4>📊 数据分析与风控</h4>
                    <ul style="font-size: 1rem; line-height: 1.8; color: #555;">
                        <li>✅ 6 项核心指标实时监控</li>
                        <li>✅ 多级预警系统（黄/红）</li>
                        <li>✅ 月度罚款金额预测</li>
                        <li>✅ 一键导出风险评估报告</li>
                    </ul>
                </div>
            </div>
        </div>
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 15px; max-width: 800px; margin: 2rem auto;">
            <h3 style="color: white;">🎯 为什么选择我们？</h3>
            <p style="font-size: 1.1rem; margin: 1rem 0;">
                全流程<strong>自动化运营</strong> · 每天仅需<strong>5分钟</strong> · 核价·库存·调价·活动·发货·售后<strong>一站式搞定</strong>
            </p>
        </div>
        <p style="color: #999; margin-top: 2rem;">
            请在左侧面板上传文件或使用示例数据开始体验 →
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; color: #999; font-size: 0.9rem;">
    <p>💡 <strong>跨境卖家运营辅助工具</strong> | 基于 2026 年 5 月最新费用规则</p>
    <p>核价·库存·调价·活动·发货·售后全流程自动化 · 每天5分钟，告别熬夜运营</p>
</div>
""", unsafe_allow_html=True)

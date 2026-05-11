import streamlit as st

def show_landing_page():
    st.set_page_config(
        page_title="Temu 商家风控与利润管家 - 产品首页",
        page_icon="💰",
        layout="wide"
    )
    
    st.markdown("""
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        
        .hero-subtitle {
            font-size: 1.5rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }
        
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            height: 100%;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .pricing-card {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }
        
        .pricing-card.popular {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            transform: scale(1.05);
        }
        
        .price-amount {
            font-size: 3rem;
            font-weight: bold;
            margin: 1rem 0;
        }
        
        .cta-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 3rem;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-block;
            margin: 1rem 0;
        }
        
        .cta-button:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        
        .stats-section {
            background: #f8f9fa;
            padding: 3rem;
            border-radius: 15px;
            margin: 3rem 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 1rem;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .testimonial-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin: 1rem 0;
        }
        
        .pain-point {
            background: #fff3cd;
            padding: 1rem;
            border-left: 4px solid #ffc107;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        
        .solution-point {
            background: #d4edda;
            padding: 1rem;
            border-left: 4px solid #28a745;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">💰 Temu 商家风控与利润管家</div>
        <div class="hero-subtitle">精确到分的费用拆分 | 实时亏损预警 | 智能罚款预测</div>
        <div style="margin-top: 2rem;">
            <a href="?page=app" class="cta-button" style="color: white; text-decoration: none;">🚀 立即体验</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_pain, col_solution = st.columns(2)
    
    with col_pain:
        st.markdown("### 😰 Temu 卖家的痛点")
        st.markdown("""
        <div class="pain-point">
            <strong>❌ 费用看不懂</strong><br>
            平台扣费有10多项：基础佣金5%-11%、物流费、支付处理费、绩效附加费...
        </div>
        <div class="pain-point">
            <strong>❌ 利润算不清</strong><br>
            日出几十单，月底一算反而亏了几千块
        </div>
        <div class="pain-point">
            <strong>❌ 罚款防不住</strong><br>
            发货超时、虚假发货、货不对版...各种罚款突如其来
        </div>
        <div class="pain-point">
            <strong>❌ 风险不知道</strong><br>
            不知道哪些SKU在亏钱，直到被罚款才后悔
        </div>
        """, unsafe_allow_html=True)
    
    with col_solution:
        st.markdown("### ✅ 我们的解决方案")
        st.markdown("""
        <div class="solution-point">
            <strong>✅ 精确费用拆分</strong><br>
            自动拆分每一项费用，精确到每个订单、每个SKU
        </div>
        <div class="solution-point">
            <strong>✅ 真实利润计算</strong><br>
            不是理论利润，是实际能到手多少钱
        </div>
        <div class="solution-point">
            <strong>✅ 智能风险预警</strong><br>
            6大风险指标实时监控，提前预警避免罚款
        </div>
        <div class="solution-point">
            <strong>✅ 数据驱动决策</strong><br>
            告诉你哪些SKU赚钱，哪些该下架
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🎯 核心功能")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 精准利润计算器</h3>
            <p style="color: #666; line-height: 1.8;">
                • 一键导入订单CSV<br>
                • 自动拆分10+项费用<br>
                • 计算真实净利润<br>
                • SKU级利润分析<br>
                • 利润率低于5%自动预警
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_f2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚠️ 智能风险监控</h3>
            <p style="color: #666; line-height: 1.8;">
                • 6大核心指标实时监控<br>
                • 多级预警系统（黄/红）<br>
                • 风险仪表盘可视化<br>
                • 智能改进建议<br>
                • 罚款金额预测
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_f3:
        st.markdown("""
        <div class="feature-card">
            <h3>📈 数据分析报告</h3>
            <p style="color: #666; line-height: 1.8;">
                • 店铺健康评分（A-F）<br>
                • 费用构成饼图<br>
                • SKU盈利排行<br>
                • 风险趋势分析<br>
                • 一键导出Excel报表
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='stats-section'>", unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        st.markdown("""
        <div class="stat-item">
            <div class="stat-number">10+</div>
            <div>费用项目拆分</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s2:
        st.markdown("""
        <div class="stat-item">
            <div class="stat-number">6</div>
            <div>风险指标监控</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s3:
        st.markdown("""
        <div class="stat-item">
            <div class="stat-number">99%</div>
            <div>计算准确率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s4:
        st.markdown("""
        <div class="stat-item">
            <div class="stat-number">5min</div>
            <div>快速上手</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 💎 定价方案")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("""
        <div class="pricing-card">
            <h3>基础版</h3>
            <div class="price-amount" style="color: #333;">¥39.9<span style="font-size: 1.2rem;">/月</span></div>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 2;">
                ✅ 利润计算功能<br>
                ✅ 基础费用拆分<br>
                ✅ CSV数据导入<br>
                ❌ 风险预警<br>
                ❌ 高级分析报告
            </ul>
            <button class="cta-button" style="background: #6c757d; padding: 0.8rem 2rem; font-size: 1rem;">选择基础版</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col_p2:
        st.markdown("""
        <div class="pricing-card popular">
            <h3>⭐ 专业版 (推荐)</h3>
            <div class="price-amount">¥99<span style="font-size: 1.2rem;">/月</span></div>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 2;">
                ✅ 所有基础版功能<br>
                ✅ 完整风险预警系统<br>
                ✅ 6大指标实时监控<br>
                ✅ 高级数据分析报告<br>
                ✅ SKU级深度分析<br>
                ✅ 优先客服支持
            </ul>
            <button class="cta-button" style="background: white; color: #667eea; padding: 0.8rem 2rem; font-size: 1rem;">立即开通</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col_p3:
        st.markdown("""
        <div class="pricing-card">
            <h3>终身版</h3>
            <div class="price-amount" style="color: #333;">¥399<span style="font-size: 1.2rem;">一次付费</span></div>
            <ul style="text-align: left; list-style: none; padding: 0; line-height: 2;">
                ✅ 所有专业版功能<br>
                ✅ 终身免费更新<br>
                ✅ 新功能优先体验<br>
                ✅ 专属客户经理<br>
                ✅ 定制化需求支持<br>
                ✅ API接口权限
            </ul>
            <button class="cta-button" style="background: #28a745; padding: 0.8rem 2rem; font-size: 1rem;">购买终身版</button>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 💳 开通方式")
    
    col_pay1, col_pay2, col_pay3 = st.columns([1, 2, 1])
    
    with col_pay2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 3rem; border-radius: 20px; text-align: center; 
                    box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
            <h3 style="margin-bottom: 1.5rem; color: #333;">📱 扫码付款，立即开通</h3>
        """, unsafe_allow_html=True)
        
        col_qr1, col_qr2 = st.columns(2)
        
        with col_qr1:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 0.5rem;">
                <p style="font-weight: bold; color: #07C160; font-size: 1.1rem; margin: 0;">
                    💚 微信支付
                </p>
            </div>
            """, unsafe_allow_html=True)

            try:
                st.image(
                    "https://raw.githubusercontent.com/erfengyuzhangsun/temutools/main/WeChat_20260512015412.png",
                    width=250,
                    caption="微信扫码付款"
                )
            except Exception as e:
                st.error(f"微信收款码加载失败：{str(e)}")
                st.markdown("📱 微信收款码（图片加载失败）")
        
        with col_qr2:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 0.5rem;">
                <p style="font-weight: bold; color: #1677FF; font-size: 1.1rem; margin: 0;">
                    💙 支付宝
                </p>
            </div>
            """, unsafe_allow_html=True)

            try:
                st.image(
                    "https://raw.githubusercontent.com/erfengyuzhangsun/temutools/main/paypal_20260512015446.jpg",
                    width=250,
                    caption="支付宝扫码付款"
                )
            except Exception as e:
                st.error(f"支付宝收款码加载失败：{str(e)}")
                st.markdown("📱 支付宝收款码（图片加载失败）")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                    margin-top: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h4 style="color: #333; margin-bottom: 1rem;">📋 开通流程</h4>
            <div style="text-align: left; line-height: 2.2; color: #555;">
                <strong>步骤 1：</strong>选择套餐，扫码付款<br>
                <strong>步骤 2：</strong>保存付款截图<br>
                <strong>步骤 3：</strong>发送截图到微信客服 <span style="color: #07C160; font-weight: bold;">temu_tools_helper</span><br>
                <strong>步骤 4：</strong>客服确认后开通账号（10分钟内）
            </div>
        </div>
        
        <div style="background: #fff3cd; padding: 1rem; border-radius: 10px; 
                    margin-top: 1.5rem; border-left: 4px solid #ffc107;">
            <strong>⏰ 服务时间：</strong>周一至周六 9:00-21:00<br>
            <strong>💡 提示：</strong>付款后请备注你的联系方式（手机号/微信号）
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 💬 用户评价")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #666; line-height: 1.8;">
                "用了这个工具才发现，我之前有好几个SKU一直在亏钱！现在每个月能多赚2000多块，真的太值了！"
            </p>
            <p><strong>— 张先生，服装类目卖家，月销500单</strong></p>
            <p style="color: #ffc107;">⭐⭐⭐⭐⭐</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t2:
        st.markdown("""
        <div class="testimonial-card">
            <p style="font-style: italic; color: #666; line-height: 1.8;">
                "最怕的就是被罚款，这个工具提前3天就预警了我的发货超时问题，帮我避免了5000多的罚款！"
            </p>
            <p><strong>— 李女士，家居百货卖家，月销800单</strong></p>
            <p style="color: #ffc107;">⭐⭐⭐⭐⭐</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    
    with col_cta2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 20px; color: white;">
            <h2 style="margin-bottom: 1rem;">🚀 立即开始，告别亏损！</h2>
            <p style="margin-bottom: 2rem; opacity: 0.9;">
                上传CSV，30秒获取完整分析报告<br>
                免费试用7天，无需信用卡
            </p>
            <a href="?page=app" class="cta-button" style="color: white; text-decoration: none;">
                📊 免费试用 →
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_faq1, col_faq2 = st.columns(2)
    
    with col_faq1:
        st.markdown("### ❓ 常见问题")
        st.markdown("""
        **Q: 支持哪些数据格式？**  
        A: 支持从Temu商家后台直接导出的CSV文件
        
        **Q: 数据安全吗？**  
        A: 所有数据本地处理，不上传到我们的服务器
        
        **Q: 费用规则会更新吗？**  
        A: 是的，我们每周更新Temu最新费用规则
        """)
    
    with col_faq2:
        st.markdown("### 📞 联系我们")
        st.markdown("""
        **微信客服：** temu_tools_helper
        **邮箱：** 484478363@qq.com
        **工作时间：** 周一至周六 9:00-21:00
        
        ---
        
        *© 2026 Temu 商家风控与利润管家 | 让每个卖家都能赚到钱*
        """)

if __name__ == "__main__":
    show_landing_page()
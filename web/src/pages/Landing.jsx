import React, { useState } from 'react';

export default function LandingPage() {
  const [showDemo, setShowDemo] = useState(false);
  const [demoStep, setDemoStep] = useState(1);
  const [orderSubmitted, setOrderSubmitted] = useState(false);

  const goLogin = () => { window.location.href = '/login'; };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 16px 32px', fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' }}>
      <style>{`
        * { box-sizing: border-box; }
        body { margin: 0; background: #fff; }
        .section-title { font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 24px; color: #333; }
        .hero {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white; padding: 50px 24px 36px; border-radius: 16px;
          text-align: center; margin-bottom: 20px; position: relative; overflow: hidden;
        }
        .hero::before {
          content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
          background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 60%);
          animation: glow 8s ease-in-out infinite;
        }
        @keyframes glow {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(10%, 10%); }
        }
        .hero * { position: relative; z-index: 1; }
        .hero-badge { font-size: 14px; opacity: 0.8; margin-bottom: 8px; }
        .hero-title { font-size: 40px; font-weight: bold; line-height: 1.3; margin-bottom: 12px; }
        .hero-desc { font-size: 18px; opacity: 0.95; line-height: 1.6; margin-bottom: 24px; }
        .hero-features { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; font-size: 14px; opacity: 0.9; margin-top: 20px; }
        .btn-primary {
          display: inline-flex; align-items: center; gap: 8px;
          background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
          color: white !important; border: none; border-radius: 35px;
          padding: 14px 36px; font-size: 18px; font-weight: bold;
          cursor: pointer; text-decoration: none !important;
          box-shadow: 0 4px 15px rgba(255,107,53,0.35);
          transition: all 0.3s ease;
        }
        .btn-primary:hover { transform: scale(1.06); box-shadow: 0 8px 24px rgba(255,107,53,0.5); }
        .btn-outline {
          display: inline-flex; align-items: center; gap: 8px;
          background: transparent; color: #667eea; border: 2px solid #667eea;
          border-radius: 35px; padding: 12px 28px; font-size: 16px; font-weight: bold;
          cursor: pointer; text-decoration: none !important;
          transition: all 0.3s ease;
        }
        .btn-outline:hover { background: #667eea; color: white; }
        .urgency {
          background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
          color: white; padding: 16px 24px; border-radius: 12px;
          text-align: center; margin-bottom: 20px;
          box-shadow: 0 4px 12px rgba(255,107,107,0.25);
        }
        .urgency h3 { margin: 0 0 6px; font-size: 18px; }
        .urgency p { margin: 0; font-size: 15px; opacity: 0.95; }
        .social-bar {
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          padding: 24px; border-radius: 12px; margin-bottom: 20px;
        }
        .stat-num { font-size: 32px; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stat-lbl { color: #666; font-size: 14px; margin-top: 4px; }
        .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
        @media (max-width: 768px) {
          .grid-4 { grid-template-columns: 1fr 1fr; }
          .grid-2 { grid-template-columns: 1fr; }
          .grid-3 { grid-template-columns: 1fr; }
          .hero-title { font-size: 28px; }
          .pricing-grid { grid-template-columns: 1fr; }
        }
        .pain {
          background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
          padding: 12px 16px; border-left: 4px solid #ffc107;
          border-radius: 8px; margin-bottom: 12px; font-size: 14px; line-height: 1.6;
          transition: all 0.3s ease;
        }
        .pain:hover { transform: translateX(-4px); box-shadow: 0 3px 10px rgba(255,193,7,0.2); }
        .sol-card {
          background: white; padding: 18px; border-radius: 12px;
          box-shadow: 0 3px 10px rgba(0,0,0,0.07); height: 100%;
          transition: all 0.3s ease; border-top: 4px solid #667eea;
        }
        .sol-card:hover { transform: translateY(-4px); box-shadow: 0 6px 18px rgba(102,126,234,0.18); }
        .sol-tag {
          display: inline-block;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white; padding: 3px 12px; border-radius: 10px;
          font-size: 13px; font-weight: bold; margin-bottom: 6px;
        }
        .sol-result {
          background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
          padding: 8px 12px; border-radius: 8px; margin-top: 8px;
          font-size: 14px; font-weight: bold; color: #155724;
        }
        .feat-card {
          background: white; padding: 20px; border-radius: 12px;
          box-shadow: 0 3px 10px rgba(0,0,0,0.08); height: 100%;
          transition: all 0.3s ease; border: 2px solid transparent;
        }
        .feat-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(102,126,234,0.18); border-color: #667eea; }
        .feat-tag {
          display: inline-block;
          background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
          color: white; padding: 4px 12px; border-radius: 12px;
          font-size: 13px; font-weight: bold; margin-bottom: 8px;
        }
        .pricing-card {
          background: white; padding: 28px 20px; border-radius: 14px;
          text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.1);
          transition: all 0.3s ease; position: relative; border: 2px solid transparent;
        }
        .pricing-card:hover { transform: translateY(-6px) scale(1.02); box-shadow: 0 10px 28px rgba(0,0,0,0.15); }
        .pricing-card.popular {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white; transform: scale(1.03);
          border: 2px solid #ffd700;
          box-shadow: 0 10px 28px rgba(102,126,234,0.35);
        }
        .pricing-card.popular::before {
          content: '⭐ 最受欢迎 · 90%卖家首选';
          position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
          background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
          color: #333; padding: 4px 20px; border-radius: 16px;
          font-weight: bold; font-size: 14px; white-space: nowrap;
          box-shadow: 0 3px 10px rgba(255,215,0,0.35);
        }
        .pricing-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; margin-top: 20px; }
        .price-amount { font-size: 40px; font-weight: bold; margin: 12px 0; }
        .price-savings { display: inline-block; background: #28a745; color: white; padding: 2px 8px; border-radius: 8px; font-size: 12px; }
        .user-tag { display: inline-block; background: #e9ecef; padding: 3px 10px; border-radius: 8px; font-size: 13px; color: #555; margin: 2px; }
        .popular .user-tag { background: rgba(255,255,255,0.2); color: white; }
        .testimonial {
          background: white; padding: 18px; border-radius: 12px;
          box-shadow: 0 3px 10px rgba(0,0,0,0.07); margin-bottom: 16px;
          border-left: 4px solid #ffc107; transition: all 0.3s ease;
        }
        .testimonial:hover { transform: translateX(6px); box-shadow: 0 6px 16px rgba(0,0,0,0.1); }
        .lifetime {
          text-align: center; margin-top: 20px; padding: 24px;
          background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
          border-radius: 14px; border: 2px dashed #667eea;
        }
        .payment-section {
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          padding: 24px; border-radius: 16px; margin-top: 20px;
          box-shadow: 0 6px 20px rgba(0,0,0,0.1); border: 2px dashed #dee2e6;
        }
        .guarantee {
          display: inline-flex; align-items: center; gap: 8px;
          background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
          color: white; padding: 10px 24px; border-radius: 20px;
          font-weight: bold; font-size: 15px;
          box-shadow: 0 3px 12px rgba(40,167,69,0.25);
        }
        .faq-section { background: #f8f9fa; padding: 20px; border-radius: 12px; }
        .faq-item { margin: 10px 0; padding: 16px; background: white; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
        .faq-q { color: #333; font-weight: bold; font-size: 15px; margin-bottom: 4px; }
        .faq-a { color: #555; font-size: 14px; line-height: 1.6; }
        .contact-card { background: white; padding: 14px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
        .demo-section {
          background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
          border-radius: 16px; padding: 24px; margin: 16px 0;
          border: 2px solid #d0d5ff;
        }
        .demo-box { background: white; border-radius: 14px; padding: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
        .mock-window { border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; background: #fff; }
        .mock-header {
          background: linear-gradient(135deg, #f0f2f5 0%, #e8ecf0 100%);
          padding: 10px 16px; border-bottom: 1px solid #e0e0e0;
          display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #444;
        }
        .mock-body { padding: 16px 20px; }
        .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }
        .dot-r { background: #ff5f56; } .dot-y { background: #ffbd2e; } .dot-g { background: #27c93f; }
        .mock-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .mock-table th { background: #f8f9fa; padding: 8px 10px; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #e0e0e0; }
        .mock-table td { padding: 7px 10px; border-bottom: 1px solid #f0f0f0; color: #333; }
        .mock-tag { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; }
        .mock-tag-s { background: #d4edda; color: #155724; }
        .mock-tag-w { background: #fff3cd; color: #856404; }
        .mock-tag-d { background: #f8d7da; color: #721c24; }
        .flex-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        @media (max-width: 600px) { .flex-2 { grid-template-columns: 1fr; } }
        .mock-col { background: #fafbfc; border: 1px solid #eee; border-radius: 8px; padding: 14px; }
        .mock-col-t { font-size: 13px; font-weight: 600; color: #667eea; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #e0e0e0; }
        .step-dots { display: flex; justify-content: center; align-items: center; gap: 8px; margin: 16px 0; }
        .step-dot { width: 10px; height: 10px; border-radius: 50%; background: #d0d5ff; cursor: pointer; transition: all 0.3s ease; }
        .step-dot.active { width: 32px; border-radius: 6px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .nav-bar {
          display: flex; justify-content: space-between; align-items: center;
          padding: 16px 0; margin-bottom: 16px;
        }
        .nav-logo { font-size: 20px; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav-links { display: flex; gap: 20px; align-items: center; }
        .nav-links a { color: #555; text-decoration: none; font-size: 14px; transition: color 0.3s; }
        .nav-links a:hover { color: #667eea; }
        .btn-login {
          background: #667eea; color: white; border: none; border-radius: 20px;
          padding: 8px 24px; font-size: 14px; font-weight: 600; cursor: pointer;
          transition: all 0.3s ease;
        }
        .btn-login:hover { background: #5a6fd6; transform: scale(1.04); }
        .divider { border: none; border-top: 1px solid #e9ecef; margin: 24px 0; }
        .cta-bottom {
          text-align: center; padding: 36px 24px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 16px; color: white;
          box-shadow: 0 10px 30px rgba(102,126,234,0.35);
        }
        .footer { text-align: center; padding: 20px 0; margin-top: 24px; border-top: 2px solid #e9ecef; color: #888; }
        .select-input {
          width: 100%; height: 40px; border-radius: 6px; border: 1px solid #d9d9d9;
          padding: 0 12px; font-size: 14px; background: white;
        }
        .text-input {
          width: 100%; height: 40px; border-radius: 6px; border: 1px solid #d9d9d9;
          padding: 0 12px; font-size: 14px;
        }
        .text-input:focus, .select-input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 2px rgba(102,126,234,0.2); }
        .form-label { font-size: 14px; font-weight: 500; margin-bottom: 6px; display: block; color: #333; }
        .form-group { margin-bottom: 16px; }
        .btn-disabled {
          display: inline-block; background: #e9ecef; color: #adb5bd;
          border: none; border-radius: 35px; padding: 10px 28px;
          font-size: 14px; font-weight: bold; cursor: not-allowed;
        }
        .annotation {
          display: flex; align-items: flex-start; gap: 8px; margin-top: 12px;
          padding: 10px 14px; background: #f0f4ff; border-radius: 8px; border: 1px dashed #667eea;
        }
        .ann-arrow {
          flex-shrink: 0; width: 28px; height: 28px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white; border-radius: 50%; display: flex; align-items: center;
          justify-content: center; font-size: 13px; font-weight: bold;
        }
        .demo-footer {
          text-align: center; padding: 12px 16px;
          background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
          border-radius: 10px; font-size: 15px; color: #444; margin-top: 16px;
          border: 1px solid #d0d5ff;
        }
      `}</style>

      {/* ==================== 导航栏 ==================== */}
      <div className="nav-bar">
        <div className="nav-logo">🤖 跨境卖家运营辅助工具</div>
        <div className="nav-links">
          <a href="#features">功能介绍</a>
          <a href="#pricing">定价方案</a>
          <a href="#faq">常见问题</a>
          <button className="btn-login" onClick={goLogin}>登录</button>
        </div>
      </div>

      {/* ==================== 1️⃣ Hero ==================== */}
      <div className="hero">
        <div className="hero-badge">🤖 跨境卖家运营辅助工具</div>
        <div className="hero-title">智能运营辅助<br />让数据帮你做决策，高效管理店铺</div>
        <div className="hero-desc">
          核价、库存、调价、活动、发货、售后一站式管理<br />
          <strong>提升运营效率，省时省力</strong>
        </div>
        <button className="btn-primary" onClick={goLogin}>🚀 免费试用3天，开启高效运营</button>
        <div className="hero-features">
          <span>✅ 助力卖家简化日常运营流程</span>
          <span>✅ 功能覆盖核价/库存/调价/活动/消息</span>
          <span>✅ 数据加密存储，保障信息安全</span>
        </div>
      </div>

      {/* 两个按钮 */}
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginBottom: 16, flexWrap: 'wrap' }}>
        <button className="btn-primary" style={{ fontSize: 16, padding: '12px 32px' }} onClick={goLogin}>🚪 免费试用3天</button>
        <button className="btn-outline" onClick={() => setShowDemo(!showDemo)}>▶ {showDemo ? '关闭演示' : '查看全功能演示'}</button>
      </div>

      {/* ==================== 演示区域 ==================== */}
      {showDemo && (
        <div className="demo-section">
          <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <h3 style={{ margin: 0, fontSize: 22, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              🤖 全功能演示 · 共10步
            </h3>
            <p style={{ color: '#555', margin: '6px 0 0', fontSize: 15 }}>覆盖运营全流程，无论是否接入API均可使用</p>
          </div>

          <div className="step-dots">
            {[1,2,3,4,5,6,7,8,9,10].map(s => (
              <div key={s} className={`step-dot ${demoStep === s ? 'active' : ''}`}
                onClick={() => setDemoStep(s)} />
            ))}
          </div>

          <div className="demo-box">
            {demoStep === 1 && (
              <>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 18, marginBottom: 16 }}>
                  <span style={{ width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 'bold' }}>1</span>
                  🔑 API密钥获取指引
                </h4>
                <div className="mock-window">
                  <div className="mock-header"><span><span className="dot dot-r"></span><span className="dot dot-y"></span><span className="dot dot-g"></span></span><span>🔑 API密钥管理 — 三步获取你的店铺密钥</span></div>
                  <div className="mock-body">
                    <div className="flex-2">
                      <div className="mock-col" style={{ border: '2px solid #667eea', background: '#f8f9ff' }}>
                        <div className="mock-col-t">📋 密钥获取3步骤</div>
                        <div style={{ padding: '8px 0', fontSize: 14 }}>
                          <div style={{ padding: '8px 10px', background: '#e8f4fd', borderRadius: 8, marginBottom: 8 }}><strong>Step 1</strong> — 登录卖家中心 → 服务市场 → 自研应用管理</div>
                          <div style={{ padding: '8px 10px', background: '#e8f4fd', borderRadius: 8, marginBottom: 8 }}><strong>Step 2</strong> — 创建自研应用，等待审核通过</div>
                          <div style={{ padding: '8px 10px', background: '#e8f4fd', borderRadius: 8 }}><strong>Step 3</strong> — 复制 App Key + App Secret + Access Token</div>
                        </div>
                      </div>
                      <div className="mock-col" style={{ border: '2px solid #667eea', background: '#f8f9ff' }}>
                        <div className="mock-col-t">🔐 填入密钥一键保存</div>
                        <div style={{ padding: '8px 0', fontSize: 14 }}>
                          <div style={{ padding: '6px 10px', background: '#f0f0f0', borderRadius: 6, marginBottom: 6 }}>App Key: <strong style={{ color: '#667eea' }}>•••••a3f8</strong></div>
                          <div style={{ padding: '6px 10px', background: '#f0f0f0', borderRadius: 6, marginBottom: 6 }}>App Secret: <strong style={{ color: '#667eea' }}>•••••f7d2</strong></div>
                          <div style={{ padding: '6px 10px', background: '#f0f0f0', borderRadius: 6, marginBottom: 6 }}>Access Token: <strong style={{ color: '#667eea' }}>•••••e4b1</strong></div>
                          <div style={{ padding: '6px', background: '#d4edda', borderRadius: 6, fontSize: 13, color: '#155724', marginTop: 6 }}>✅ 加密存储，安全可靠</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="annotation"><div className="ann-arrow">①</div><div><strong>不会API密钥申请？</strong> — 进入应用后「API密钥管理」页有完整图文指引</div></div>
                <div className="annotation"><div className="ann-arrow">②</div><div><strong>没有密钥也能用！</strong> — 系统内置模拟数据模式，不填密钥即可体验全部功能</div></div>
                <div className="demo-footer">💡 <strong>提示：</strong>系统中所有API密钥使用加密存储，安全可靠。无密钥也可使用Mock模式体验全部功能</div>
              </>
            )}
            {demoStep === 2 && (
              <>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 18, marginBottom: 16 }}>
                  <span style={{ width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 'bold' }}>2</span>
                  🏭 工厂成本管理
                </h4>
                <div className="mock-window">
                  <div className="mock-header"><span><span className="dot dot-r"></span><span className="dot dot-y"></span><span className="dot dot-g"></span></span><span>🏭 工厂成本管理 — 产品资料录入与供货价测算</span></div>
                  <div className="mock-body">
                    <div className="flex-2">
                      <div className="mock-col" style={{ border: '2px solid #667eea', background: '#f8f9ff' }}>
                        <div className="mock-col-t">📋 产品录入表</div>
                        <table className="mock-table">
                          <tr><th>SKU</th><th>产品名称</th><th>材料成本</th><th>人工</th><th>总成本</th></tr>
                          <tr><td>C001</td><td>智能保温杯</td><td>¥12.50</td><td>¥3.00</td><td>¥18.50</td></tr>
                          <tr><td>C002</td><td>无线充电器</td><td>¥22.00</td><td>¥4.50</td><td>¥29.80</td></tr>
                        </table>
                      </div>
                      <div className="mock-col" style={{ border: '2px solid #667eea', background: '#f8f9ff' }}>
                        <div className="mock-col-t">📊 成本分析</div>
                        <div style={{ padding: '8px 0', fontSize: 14 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span style={{ color: '#666' }}>建议供货价</span><strong style={{ color: '#667eea' }}>¥28.50</strong></div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span style={{ color: '#666' }}>期望毛利率</span><strong style={{ color: '#28a745' }}>35%</strong></div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span style={{ color: '#666' }}>安全调价区间</span><strong>¥25.00 - ¥32.00</strong></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="demo-footer">💡 <strong>效果：</strong>零API依赖，输入成本即出建议供货价，辅助核价决策</div>
              </>
            )}
            {demoStep === 3 && (
              <>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 18, marginBottom: 16 }}>
                  <span style={{ width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 'bold' }}>3</span>
                  🧮 全托管核价引擎
                </h4>
                <div className="mock-window">
                  <div className="mock-header"><span><span className="dot dot-r"></span><span className="dot dot-y"></span><span className="dot dot-g"></span></span><span>🧮 核价引擎 — 成本→供货价全自动测算</span></div>
                  <div className="mock-body">
                    <div className="flex-2">
                      <div className="mock-col" style={{ border: '2px solid #667eea', background: '#f8f9ff' }}>
                        <div className="mock-col-t">💰 成本参数输入</div>
                        <div style={{ padding: '8px 0', fontSize: 14 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span>产品成本</span><strong>¥18.50</strong></div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span>平台佣金</span><strong>5.5%</strong></div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span>目的毛利率</span><strong>25%</strong></div>
                        </div>
                      </div>
                      <div className="mock-col" style={{ border: '2px solid #667eea', background: '#f8f9ff' }}>
                        <div className="mock-col-t">📊 测算结果</div>
                        <div style={{ padding: '8px 0', fontSize: 14 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span>建议供货价</span><strong style={{ color: '#667eea' }}>¥26.07</strong></div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span>净利润</span><strong style={{ color: '#28a745' }}>¥6.52 (25%)</strong></div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}><span>调价区间</span><strong>¥24.50 - ¥28.00</strong></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="demo-footer">💡 <strong>效果：</strong>零API依赖，输入成本即出建议供货价，辅助核价决策</div>
              </>
            )}
            {demoStep === 4 && (
              <>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 18, marginBottom: 16 }}>
                  <span style={{ width: 32, height: 32, borderRadius: '50%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 'bold' }}>4</span>
                  🛡️ 风控防二次核价
                </h4>
                <div className="mock-window">
                  <div className="mock-header"><span><span className="dot dot-r"></span><span className="dot dot-y"></span><span className="dot dot-g"></span></span><span>🛡️ 风控规则引擎 — 调价前自动检测风险</span></div>
                  <div className="mock-body">
                    <div className="flex-2">
                      <div className="mock-col" style={{ border: '2px solid #dc3545', background: '#fff5f5' }}>
                        <div className="mock-col-t" style={{ color: '#dc3545' }}>⚠️ 本次调价拦截报告</div>
                        <div style={{ background: '#fff0f0', borderLeft: '3px solid #dc3545', padding: '6px 10px', borderRadius: 4, fontSize: 13, marginBottom: 6, color: '#721c24' }}>
                          <strong>🚫 规则R001：毛利率低于安全线</strong><br />调价后毛利率12.5% &lt; 安全线15.0%
                        </div>
                        <div style={{ background: '#fff0f0', borderLeft: '3px solid #dc3545', padding: '6px 10px', borderRadius: 4, fontSize: 13, color: '#721c24' }}>
                          <strong>🚫 规则R003：频繁调价触发风控</strong><br />24小时内调价3次 &gt; 最大允许2次
                        </div>
                      </div>
                      <div className="mock-col" style={{ border: '2px solid #28a745', background: '#f5fff5' }}>
                        <div className="mock-col-t" style={{ color: '#28a745' }}>📋 风控规则（6条内置）</div>
                        <div style={{ fontSize: 13, marginBottom: 4 }}>✅ R001 毛利率低于安全线 — 已开启</div>
                        <div style={{ fontSize: 13, marginBottom: 4 }}>✅ R002 单次调价幅度超限 — 已开启</div>
                        <div style={{ fontSize: 13 }}>✅ R003~R006 其他规则 — 已开启</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="demo-footer">💡 <strong>效果：</strong>全部调价操作先过风控再执行，守住利润底线</div>
              </>
            )}
            {demoStep >= 5 && (
              <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                <div style={{ fontSize: 48, marginBottom: 16 }}>
                  {['','','','','📊','⚡','🚨','🎯','💬','📈'][demoStep]}
                </div>
                <h3 style={{ fontSize: 20, marginBottom: 8, color: '#333' }}>
                  {['','','','','自动核价处理','智能调价管理','库存预警管理','活动自动报名','消息与售后管理','数据大屏与报表'][demoStep]}
                </h3>
                <p style={{ color: '#666', fontSize: 15, marginBottom: 20 }}>进入应用后即可体验完整功能，无API密钥也可使用Mock模式</p>
                <button className="btn-primary" style={{ fontSize: 16, padding: '12px 32px' }} onClick={goLogin}>🚀 立即免费试用</button>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12 }}>
            <button className="btn-outline" style={{ padding: '8px 24px', fontSize: 14, opacity: demoStep <= 1 ? 0.4 : 1 }}
              disabled={demoStep <= 1} onClick={() => setDemoStep(d => d - 1)}>← 上一步</button>
            <button className="btn-primary" style={{ padding: '8px 24px', fontSize: 14 }}
              onClick={() => demoStep < 10 ? setDemoStep(d => d + 1) : setShowDemo(false)}>
              {demoStep < 10 ? '下一步 →' : '完成演示'}
            </button>
          </div>
        </div>
      )}

      {/* ==================== 2️⃣ 紧迫感横幅 ==================== */}
      <div className="urgency">
        <h3>🎉 累计服务800+卖家，首发专属：前 <strong>100</strong> 名新用户享 <strong>8折</strong></h3>
        <p>专业版原价 ¥199/季度，现价 <strong style={{ fontSize: 17 }}>¥169/季度</strong> | 仅剩 <strong style={{ color: '#FFE66D', fontSize: 17 }}>23</strong> 个名额 | ⏰ 截止：2026年6月30日</p>
      </div>

      {/* ==================== 3️⃣ 社会证明 ==================== */}
      <div className="social-bar">
        <div className="grid-4">
          <div style={{ textAlign: 'center', padding: 8 }}><div className="stat-num">800+</div><div className="stat-lbl">👥 累计合作卖家</div></div>
          <div style={{ textAlign: 'center', padding: 8 }}><div className="stat-num">高效</div><div className="stat-lbl">🤖 智能辅助运营管理</div></div>
          <div style={{ textAlign: 'center', padding: 8 }}><div className="stat-num">¥3000+</div><div className="stat-lbl">💰 单店月均节省成本</div></div>
          <div style={{ textAlign: 'center', padding: 8 }}><div className="stat-num">4.9/5</div><div className="stat-lbl">⭐ 用户满意度</div></div>
        </div>
      </div>

      <hr className="divider" />

      {/* ==================== 4️⃣ 痛点 ==================== */}
      <h2 className="section-title">😰 这些Temu运营难题，你中了几个？</h2>
      <div className="grid-2">
        <div>
          <div className="pain"><strong>❓ 每天手动核价、算利润，算到凌晨还在亏？</strong><br />核价通知一来就紧张，手动算半天还怕算错，月底一结算发现白干</div>
          <div className="pain"><strong>❓ 竞品降价手动跟价，反应慢就丢单，还守不住毛利？</strong><br />不跟→没单，跟了→亏本，手动盯价格盯到眼睛疼</div>
          <div className="pain"><strong>❓ 库存断货/滞销，一边亏流量一边压资金？</strong><br />爆款断货丢排名，滞销品堆在仓库天天亏仓储费</div>
        </div>
        <div>
          <div className="pain"><strong>❓ 活动报名错过时间，大促活动只能看着别人爆单？</strong><br />活动通知太多看不过来，等想起来报名已经截止</div>
          <div className="pain"><strong>❓ 售后消息、处罚通知漏看，店铺分一路掉？</strong><br />一天几百条消息，重要通知被淹没，漏看一条就扣分罚款</div>
          <div className="pain"><strong>❓ 数据报表要做1小时，还找不到问题在哪？</strong><br />每天花大量时间做表，做完也不知道该优化哪里</div>
        </div>
      </div>

      <hr className="divider" />

      {/* ==================== 5️⃣ 解决方案 ==================== */}
      <h2 className="section-title" id="features">🚀 全流程辅助，每个环节都帮你提效</h2>
      {[
        [{ name: '全自动核价', tag: '智能核价提醒，避免遗漏，轻松管理', pain: '手动核价30分钟，还漏处理导致商品下架', solution: '按预设毛利规则批量自动处理核价通知，超时强提醒', result: '节省运营时间，降低遗漏风险' },
         { name: '库存智能管理', tag: '防断货、防积压，资金和流量双保住', pain: '断货丢流量，滞销压资金', solution: '安全库存预警+销量预测+滞销SKU识别，自动生成补货建议', result: '智能库存管理，优化资金周转' }],
        [{ name: '智能自动调价', tag: '跟价不亏，守住每一分利润', pain: '跟价就亏，不跟价就没单', solution: '竞品实时监控+保本毛利锁定+活动价定时切换', result: '保毛利前提下自动跟价，助力利润优化' },
         { name: '活动自动报名', tag: '一键匹配，轻松参与活动', pain: '手动找活动、筛选SKU，错过报名时间', solution: '自动抓取可报活动+SKU匹配+批量报名+状态追踪', result: '不错过报名机会' }],
        [{ name: '数据自动分析与预警', tag: '自动找问题，快速掌握店铺状态', pain: '做报表1小时，还找不到问题', solution: '每日自动生成报表，异常指标实时预警，给出优化建议', result: '批量处理，快速出结果' },
         { name: '消息与售后自动化', tag: '集中管理，减少遗漏', pain: '消息太多看不过来，处罚通知漏看', solution: '消息智能分类+重要通知强提醒+售后模板一键复用', result: '集中管理通知，减少遗漏' }],
        [{ name: '标签与发货自动化', tag: '批量处理发货流程，节省时间', pain: '手动生成标签1小时，容易出错', solution: '批量生成平台规范标签/箱唛，同步物流信息', result: '压缩到20分钟内完成' },
         { name: '多店铺统一总控', tag: '一个后台管所有店', pain: '多店铺来回切换后台，信息混乱', solution: '一个后台管理所有店铺，盈亏/待办/告警一站式查看', result: '多店运营效率提升60%' }],
      ].map((row, ri) => (
        <div key={ri} className="grid-2" style={{ marginBottom: 16 }}>
          {row.map((item, ci) => (
            <div key={ci} className="sol-card">
              <div className="sol-tag">{item.tag}</div>
              <h3 style={{ margin: '6px 0 10px', fontSize: 17, color: '#333' }}>{item.name}</h3>
              <div style={{ fontSize: 14, lineHeight: 1.7 }}>
                <div style={{ color: '#dc3545', marginBottom: 6 }}>😖 <strong>痛点：</strong>{item.pain}</div>
                <div style={{ color: '#667eea', marginBottom: 6 }}>🛠 <strong>方案：</strong>{item.solution}</div>
              </div>
              <div className="sol-result">📈 结果：{item.result}</div>
            </div>
          ))}
        </div>
      ))}

      <hr className="divider" />

      {/* ==================== 6️⃣ 核心功能 ==================== */}
      <h2 className="section-title">🎯 核心功能</h2>
      <div className="grid-3">
        {[
          { icon: '📊', name: '全自动核价模块', tag: '智能核价提醒，避免遗漏，轻松管理', items: ['🔄 批量导入订单自动匹配核价规则', '🤖 按预设毛利自动接受/拒绝', '⏰ 超时未处理自动强提醒，不漏单', '📉 利润低于阈值自动拦截'] },
          { icon: '📦', name: '库存智能管理', tag: '防断货、防积压，资金和流量双保住', items: ['📈 库存销量趋势实时追踪', '🚨 安全库存预警，断货前自动提醒', '📉 滞销SKU自动识别+清仓建议', '📄 自动生成补货建议单'] },
          { icon: '📈', name: '智能自动调价', tag: '跟价不亏，守住每一分利润', items: ['🔎 竞品价格实时监控', '🔒 保本毛利底线锁定', '📅 活动价/日常价定时切换', '📋 调价历史全记录'] },
        ].map((f, i) => (
          <div key={i} className="feat-card">
            <div className="feat-tag">{f.tag}</div>
            <h3 style={{ color: '#667eea', margin: '12px 0 8px', fontSize: 17 }}>{f.icon} {f.name}</h3>
            <p style={{ color: '#555', lineHeight: 1.8, fontSize: 14 }}>{f.items.map((it, j) => <React.Fragment key={j}>• {it}<br /></React.Fragment>)}</p>
          </div>
        ))}
      </div>
      <div className="grid-3" style={{ marginTop: 16 }}>
        {[
          { icon: '🎯', name: '平台活动自动报名', tag: '一键匹配，轻松参与活动', items: ['🔍 自动抓取可报名活动', '📋 一键批量报名', '📊 活动状态追踪', '⏰ 报名截止前自动提醒'] },
          { icon: '📈', name: '数据自动分析与预警', tag: '自动找问题，快速掌握店铺状态', items: ['📋 每日自动生成运营日报', '🚨 异常指标实时预警', '📊 趋势图表可视化', '📄 一键导出报表'] },
          { icon: '🏢', name: '多店铺总控大屏', tag: '一个后台管所有店', items: ['🖥 一个后台管理所有店铺', '💰 多店盈亏一站式查看', '📊 各店数据横向对比', '🔒 数据严格隔离'] },
        ].map((f, i) => (
          <div key={i} className="feat-card">
            <div className="feat-tag">{f.tag}</div>
            <h3 style={{ color: '#667eea', margin: '12px 0 8px', fontSize: 17 }}>{f.icon} {f.name}</h3>
            <p style={{ color: '#555', lineHeight: 1.8, fontSize: 14 }}>{f.items.map((it, j) => <React.Fragment key={j}>• {it}<br /></React.Fragment>)}</p>
          </div>
        ))}
      </div>

      <hr className="divider" />

      {/* ==================== 7️⃣ 用户评价 ==================== */}
      <h2 className="section-title">💬 卖家真实反馈</h2>
      <p style={{ textAlign: 'center', color: '#666', fontSize: 15, marginBottom: 20 }}>
        已助力 <strong style={{ color: '#667eea' }}>众多</strong> 卖家提升运营效率
      </p>
      <div className="grid-2">
        <div>
          <div className="testimonial">
            <p style={{ fontStyle: 'italic', color: '#555', lineHeight: 1.7, fontSize: 15, margin: 0 }}>
              "以前每天运营要花<strong>3小时</strong>，现在每天看告警和管理数据，每月省了大量时间，<strong style={{ color: '#28a745' }}>利润明显提升</strong>！"
            </p>
            <p style={{ marginTop: 10, fontSize: 14 }}><strong>— 服装类目卖家 · 张先生</strong> <span style={{ color: '#888' }}>| 月销500单</span></p>
            <p style={{ color: '#ffc107', fontSize: 16, marginTop: 4 }}>⭐⭐⭐⭐⭐ 使用3个月</p>
          </div>
          <div className="testimonial">
            <p style={{ fontStyle: 'italic', color: '#555', lineHeight: 1.7, fontSize: 15, margin: 0 }}>
              "一个后台管5家店，不用来回切换后台，<strong>运营效率明显提升</strong>，<strong style={{ color: '#667eea' }}>多店卖家必备</strong>"
            </p>
            <p style={{ marginTop: 10, fontSize: 14 }}><strong>— 多店卖家 · 陈经理</strong> <span style={{ color: '#888' }}>| 5家店铺</span></p>
            <p style={{ color: '#ffc107', fontSize: 16, marginTop: 4 }}>⭐⭐⭐⭐⭐ 使用6个月</p>
          </div>
        </div>
        <div>
          <div className="testimonial">
            <p style={{ fontStyle: 'italic', color: '#555', lineHeight: 1.7, fontSize: 15, margin: 0 }}>
              "自动调价帮我守住了毛利，以前跟价就亏，现在<strong>保毛利前提下自动跟价</strong>，<strong style={{ color: '#28a745' }}>再也不亏着卖了</strong>！"
            </p>
            <p style={{ marginTop: 10, fontSize: 14 }}><strong>— 家居类目卖家 · 李女士</strong> <span style={{ color: '#888' }}>| 月销800单</span></p>
            <p style={{ color: '#ffc107', fontSize: 16, marginTop: 4 }}>⭐⭐⭐⭐⭐ 使用2个月</p>
          </div>
          <div className="testimonial">
            <p style={{ fontStyle: 'italic', color: '#555', lineHeight: 1.7, fontSize: 15, margin: 0 }}>
              "刚做Temu什么都不懂，工具帮我自动核价、算利润，避开了好几次罚款，<strong style={{ color: '#28a745' }}>3个月从月亏到月赚3000+</strong>"
            </p>
            <p style={{ marginTop: 10, fontSize: 14 }}><strong>— 新手卖家 · 王老板</strong> <span style={{ color: '#888' }}>| 3C数码 | 月销300单</span></p>
            <p style={{ color: '#ffc107', fontSize: 16, marginTop: 4 }}>⭐⭐⭐⭐⭐ 使用1个月</p>
          </div>
        </div>
      </div>

      <hr className="divider" />

      {/* ==================== 8️⃣ 定价方案 ==================== */}
      <h2 className="section-title" id="pricing">💎 选择适合你的套餐</h2>
      <div className="pricing-grid">
        <div className="pricing-card">
          <div style={{ marginBottom: 8 }}><span className="user-tag">👤 新手卖家</span><span className="user-tag">📦 单店小卖家</span></div>
          <h3 style={{ marginBottom: 4 }}>基础版</h3>
          <p style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>搞定利润核算和基础风控</p>
          <div className="price-amount" style={{ color: '#333' }}>¥69<span style={{ fontSize: 18 }}>/月</span></div>
          <p style={{ fontSize: 13, color: '#888' }}>年付 ¥588/年（省30%）</p>
          <ul style={{ textAlign: 'left', listStyle: 'none', padding: 0, lineHeight: 2.2, color: '#555', margin: '16px 0', fontSize: 14 }}>
            <li>✅ 精准利润计算器</li><li>✅ 基础核价自动化</li><li>✅ 库存预警+基础数据分析</li><li>✅ 7×12小时客服支持</li>
          </ul>
          <span className="btn-disabled">选择基础版</span>
        </div>

        <div className="pricing-card popular">
          <div style={{ marginBottom: 8 }}><span className="user-tag">👤 稳定出单卖家</span><span className="user-tag">🏪 多店卖家</span></div>
          <h3 style={{ marginBottom: 4 }}>专业版</h3>
          <p style={{ fontSize: 13, opacity: 0.85, marginBottom: 8 }}>全流程辅助，轻松管理运营</p>
          <div className="price-amount">¥169<span style={{ fontSize: 18 }}>/季度</span><br /><span className="price-savings">省15%</span></div>
          <p style={{ fontSize: 14, opacity: 0.9, margin: '6px 0' }}>原价 ¥199/季度 | 限时85折</p>
          <ul style={{ textAlign: 'left', listStyle: 'none', padding: 0, lineHeight: 2.2, opacity: 0.95, margin: '16px 0', fontSize: 14 }}>
            <li>✅ 包含所有基础版功能</li><li>✅ 智能辅助模块（核价/库存/调价/活动/消息）</li><li>✅ 多店铺统一管理</li><li>✅ 优先客服支持</li>
          </ul>
          <p style={{ fontSize: 14, fontWeight: 'bold', opacity: 0.9 }}>🔥 高效运营的必备方案</p>
          <span className="btn-disabled" style={{ background: 'rgba(255,255,255,0.2)', color: 'white', opacity: 0.65 }}>🎯 立即订阅</span>
        </div>

        <div className="pricing-card">
          <div style={{ marginBottom: 8 }}><span className="user-tag">👤 规模化卖家</span><span className="user-tag">👥 企业团队</span></div>
          <h3 style={{ marginBottom: 4 }}>企业版</h3>
          <p style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>多店矩阵管理，全方位运营覆盖</p>
          <div className="price-amount" style={{ color: '#333' }}>¥399<span style={{ fontSize: 18 }}>/月</span></div>
          <p style={{ fontSize: 13, color: '#888' }}>年付 ¥3999/年（省16%）</p>
          <ul style={{ textAlign: 'left', listStyle: 'none', padding: 0, lineHeight: 2.2, color: '#555', margin: '16px 0', fontSize: 14 }}>
            <li>✅ 包含所有专业版功能</li><li>✅ 工厂成本管理+供应链协同</li><li>✅ 10+店铺统一管理</li><li>✅ API优先调用+专属客户经理</li>
          </ul>
          <span className="btn-disabled">选择企业版</span>
        </div>
      </div>

      <div className="lifetime">
        <h3 style={{ margin: '0 0 6px', color: '#667eea', fontSize: 20 }}>🏆 终身版 · 限时特惠</h3>
        <p style={{ color: '#555', margin: '6px 0', fontSize: 15 }}>一次付费，永久使用！终身免费更新+新功能优先体验</p>
        <div style={{ fontSize: 34, fontWeight: 'bold', color: '#28a745', margin: '8px 0' }}>
          ¥1,999 <span style={{ fontSize: 16, color: '#888', textDecoration: 'line-through' }}>¥4,788</span>
        </div>
        <p style={{ color: '#888', fontSize: 13 }}>相当于专业版不到1年的费用，永久使用 | 限前50名</p>
        <span className="btn-disabled" style={{ background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)', color: 'white', opacity: 0.65, padding: '12px 40px', fontSize: 16 }}>🏆 抢购终身版</span>
      </div>

      {/* 收款码+订单 */}
      <div className="payment-section" id="payment">
        <h3 style={{ textAlign: 'center', color: '#333', marginBottom: 20, fontSize: 20 }}>💰 选择套餐，立即开通</h3>
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <span className="guarantee">✅ 7天无理由退款保证 | 不满意全额退款</span>
        </div>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: 20, fontSize: 15 }}>支持微信 / 支付宝，付款后 10 分钟内开通账号</p>

        <div className="grid-2" style={{ marginBottom: 24 }}>
          <div style={{ textAlign: 'center', padding: 20, background: 'white', borderRadius: 12, boxShadow: '0 3px 10px rgba(0,0,0,0.07)' }}>
            <div style={{ fontWeight: 'bold', fontSize: 16, marginBottom: 12, color: '#07C160' }}>💚 微信支付</div>
            <img src="/payment/wechat.png" alt="微信收款码" style={{ width: 230, height: 230, objectFit: 'contain', borderRadius: 8 }} />
            <p style={{ color: '#888', fontSize: 13, marginTop: 8 }}>微信扫码付款</p>
          </div>
          <div style={{ textAlign: 'center', padding: 20, background: 'white', borderRadius: 12, boxShadow: '0 3px 10px rgba(0,0,0,0.07)' }}>
            <div style={{ fontWeight: 'bold', fontSize: 16, marginBottom: 12, color: '#1677FF' }}>💙 支付宝</div>
            <img src="/payment/alipay.jpg" alt="支付宝收款码" style={{ width: 230, height: 230, objectFit: 'contain', borderRadius: 8 }} />
            <p style={{ color: '#888', fontSize: 13, marginTop: 8 }}>支付宝扫码付款</p>
          </div>
        </div>

        <hr className="divider" />

        <div style={{ background: 'white', padding: 20, borderRadius: 12, boxShadow: '0 3px 10px rgba(0,0,0,0.06)' }}>
          <h4 style={{ color: '#333', marginBottom: 16, textAlign: 'center', fontSize: 17 }}>📋 提交订单（付款后填写）</h4>

          {!orderSubmitted ? (
            <form onSubmit={async (e) => {
              e.preventDefault();
              const form = e.target;
              const data = {
                plan_name: form.plan_name.value,
                contact_name: form.contact_name.value,
                phone: form.phone.value,
                wechat: form.wechat.value,
                notes: form.notes.value,
              };
              try {
                await fetch('/api/v1/submit-order', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(data),
                });
              } catch {}
              setOrderSubmitted(true);
            }}>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">选择套餐</label>
                  <select className="select-input" name="plan_name" required>
                    <option value="">-- 请选择套餐 --</option>
                    <option>基础版 - ¥69/月</option>
                    <option>专业版 - ¥169/季度（推荐）</option>
                    <option>企业版 - ¥399/月</option>
                    <option>终身版 - ¥1999</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">您的姓名</label>
                  <input className="text-input" name="contact_name" placeholder="请输入联系人姓名" required />
                </div>
              </div>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">手机号</label>
                  <input className="text-input" name="phone" placeholder="请输入手机号" required />
                </div>
                <div className="form-group">
                  <label className="form-label">微信号（选填）</label>
                  <input className="text-input" name="wechat" placeholder="微信号，方便客服联系" />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">备注（选填）</label>
                <textarea name="notes" style={{ width: '100%', borderRadius: 6, border: '1px solid #d9d9d9', padding: 10, fontSize: 14 }} rows={2} placeholder="如有特殊需求请在此说明..." />
              </div>
              <div style={{ textAlign: 'center' }}>
                <button className="btn-primary" style={{ fontSize: 16, padding: '12px 40px' }} type="submit">✅ 我已付款，提交订单</button>
              </div>
            </form>
          ) : (
            <div style={{ background: 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)', border: '2px solid #28a745', padding: 24, borderRadius: 12, textAlign: 'center' }}>
              <h3 style={{ margin: '0 0 12px', color: '#28a745', fontSize: 22 }}>🎉 订单提交成功！</h3>
              <p style={{ margin: '6px 0', color: '#155724', fontSize: 16, lineHeight: 1.8 }}>
                感谢您选择我们的服务！<br />我们将在 <strong style={{ color: '#dc3545' }}>10分钟内</strong> 通过手机号联系您<br />如需加急，请添加微信：<strong style={{ color: '#07C160' }}>returnHuangMuNing</strong>
              </p>
              <button className="btn-outline" style={{ marginTop: 12 }} onClick={() => setOrderSubmitted(false)}>📝 提交新订单</button>
            </div>
          )}
        </div>
      </div>

      <hr className="divider" />

      {/* ==================== 9️⃣ 最终CTA ==================== */}
      <div className="cta-bottom">
        <h2 style={{ color: 'white', marginBottom: 8, fontSize: 26 }}>🚀 高效运营，轻松管理</h2>
        <p style={{ marginBottom: 16, fontSize: 15, opacity: 0.95, lineHeight: 1.6 }}>
          核价、库存、调价、活动、发货一站式管理<br />
          把时间花在选品和业务上，而不是盯后台做报表<br />
          <span style={{ fontSize: 14 }}>✅ 免费试用 3 天 | ✅ 无需信用卡 | ✅ 随时可取消</span>
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn-primary" style={{ fontSize: 17, padding: '14px 36px' }} onClick={goLogin}>🚀 免费试用3天 →</button>
          <button className="btn-outline" style={{ color: 'white', borderColor: 'rgba(255,255,255,0.7)' }}
            onClick={() => document.getElementById('payment')?.scrollIntoView({ behavior: 'smooth' })}>
            💰 查看定价方案
          </button>
        </div>
      </div>

      <hr className="divider" />

      {/* ==================== 🔟 FAQ + 联系方式 ==================== */}
      <div className="grid-2" id="faq" style={{ gap: 24 }}>
        <div className="faq-section">
          <h3 style={{ marginBottom: 16, fontSize: 18 }}>❓ 常见问题</h3>
          {[
            { q: 'Q: 自动化核价会不会误处理，导致我亏损？', a: 'A: 所有核价操作都按您预设的毛利规则执行，支持日常/活动双阈值，可手动干预，操作全留日志可溯源，<strong>不会误处理</strong>。' },
            { q: 'Q: 数据安全吗？会不会泄露我的店铺数据？', a: 'A: 店铺数据本地加密存储，API密钥不上云，所有操作留日志可溯源，<strong>不会上传您的店铺隐私数据</strong>。' },
            { q: 'Q: 多店铺支持吗？会不会操作混乱？', a: 'A: 支持多店铺统一管理，一个后台查看所有店铺的盈亏、待办和告警，<strong>数据严格隔离，不会混乱</strong>。' },
            { q: 'Q: 我是新手，不会用怎么办？', a: 'A: 提供详细的使用教程+专属客服支持，<strong>7×12小时在线答疑</strong>，新手也能快速上手。' },
          ].map((item, i) => (
            <div key={i} className="faq-item">
              <div className="faq-q">{item.q}</div>
              <div className="faq-a" dangerouslySetInnerHTML={{ __html: item.a }} />
            </div>
          ))}
        </div>
        <div className="faq-section">
          <h3 style={{ marginBottom: 16, fontSize: 18 }}>📞 联系我们</h3>
          <div className="contact-card">
            <div style={{ fontSize: 15, color: '#333', fontWeight: 'bold', marginBottom: 4 }}>💬 微信客服</div>
            <div style={{ fontSize: 16, fontWeight: 'bold', color: '#07C160' }}>returnHuangMuNing</div>
            <div style={{ fontSize: 13, color: '#888', marginTop: 4 }}>添加好友后发送「咨询」即可</div>
          </div>
          <div className="contact-card">
            <div style={{ fontSize: 15, color: '#333', fontWeight: 'bold', marginBottom: 4 }}>📧 邮箱联系</div>
            <div style={{ fontSize: 16, fontWeight: 'bold', color: '#667eea' }}>484478363@qq.com</div>
            <div style={{ fontSize: 13, color: '#888', marginTop: 4 }}>24小时内回复</div>
          </div>
          <div className="contact-card">
            <div style={{ fontSize: 15, color: '#333', fontWeight: 'bold', marginBottom: 4 }}>⏰ 工作时间</div>
            <div style={{ fontSize: 16, fontWeight: 'bold', color: '#333' }}>周一至周六 9:00 - 21:00</div>
            <div style={{ fontSize: 13, color: '#888', marginTop: 4 }}>节假日可能延迟回复</div>
          </div>
        </div>
      </div>

      <div className="footer">
        <p style={{ margin: '4px 0', fontSize: 14 }}>© 2026 跨境卖家运营辅助工具 | 专注数据与运营管理 🤖</p>
        <p style={{ margin: '4px 0', fontSize: 13, color: '#aaa' }}>本工具仅用于辅助商家进行数据分析和运营决策，不构成任何投资建议</p>
      </div>
    </div>
  );
}

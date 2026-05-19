import React, { useState, useEffect } from 'react';

export default function LandingPage() {
  const [flash, setFlash] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const success = params.get('success');
    const error = params.get('error');
    if (success) {
      setFlash({ type: 'success', text: decodeURIComponent(success) });
    } else if (error) {
      setFlash({ type: 'error', text: decodeURIComponent(error) });
    }
    if (success || error) {
      const url = new URL(window.location.href);
      url.searchParams.delete('success');
      url.searchParams.delete('error');
      window.history.replaceState({}, '', url.pathname + url.hash);
    }
  }, []);

  const goLogin = () => { window.location.href = '/login'; };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 16px 32px', fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' }}>
      <style>{`
        body { margin: 0; background: #fff; }
        .hero {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white; padding: 48px 24px 36px; border-radius: 16px;
          text-align: center; margin-bottom: 20px;
        }
        .hero-title { font-size: 36px; font-weight: bold; line-height: 1.3; margin-bottom: 12px; }
        .hero-desc { font-size: 17px; opacity: 0.95; line-height: 1.6; margin-bottom: 24px; }
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
        .section-title { font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 20px; color: #333; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
        @media (max-width: 768px) {
          .grid-3 { grid-template-columns: 1fr; }
          .hero-title { font-size: 26px; }
        }
        .feat-card {
          background: white; padding: 20px; border-radius: 12px;
          box-shadow: 0 3px 10px rgba(0,0,0,0.08); height: 100%;
          transition: all 0.3s ease; border: 2px solid transparent;
        }
        .feat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(102,126,234,0.18); border-color: #667eea; }
        .footer { text-align: center; padding: 20px 0; margin-top: 24px; border-top: 2px solid #e9ecef; color: #888; }
        .divider { border: none; border-top: 1px solid #e9ecef; margin: 20px 0; }
        .status-badge {
          display: inline-block; padding: 6px 16px; border-radius: 20px;
          font-size: 14px; font-weight: bold; margin-bottom: 12px;
        }
      `}</style>

      {flash && (
        <div style={{
          margin: '12px 0', padding: '14px 18px', borderRadius: 10, fontSize: 15, lineHeight: 1.6,
          background: flash.type === 'success' ? '#d4edda' : '#f8d7da',
          color: flash.type === 'success' ? '#155724' : '#721c24',
          border: `1px solid ${flash.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`,
        }}>
          {flash.type === 'success' ? '✅ ' : '⚠️ '}{flash.text}
          {flash.type === 'success' && (
            <span> — <a href="/login" style={{ color: '#155724', fontWeight: 'bold' }}>立即登录</a> 进入系统</span>
          )}
        </div>
      )}

      <div className="nav-bar">
        <div className="nav-logo">鲸云策</div>
        <div className="nav-links">
          <a href="#features">功能介绍</a>
          <button className="btn-login" onClick={goLogin}>登录</button>
        </div>
      </div>

      <div className="hero">
        <div className="hero-title">Temu 全托管卖家运营辅助工具</div>
        <div className="hero-desc">
          核价、库存、成本管理一站式辅助<br />
          正在开发中，敬请期待
        </div>
        <button className="btn-primary" onClick={goLogin}>进入系统</button>
      </div>

      <hr className="divider" />

      <h2 className="section-title" id="features">功能介绍</h2>
      <div className="grid-3">
        {[
          { icon: '🧮', name: '核价管理', desc: '核价通知查询、自动处理、历史记录' },
          { icon: '📦', name: '库存管理', desc: '库存列表查看、库存同步' },
          { icon: '💰', name: '工厂成本', desc: '产品资料录入、成本分析、建议供货价测算' },
          { icon: '🛡️', name: '风控引擎', desc: '调价前自动检测毛利率、频率等风险' },
          { icon: '📊', name: '数据分析', desc: '经营指标采集、趋势分析、报表导出' },
          { icon: '💳', name: '财务结算', desc: '结算同步、月度汇总、预测分析' },
        ].map((f, i) => (
          <div key={i} className="feat-card">
            <div style={{ fontSize: 28, marginBottom: 8 }}>{f.icon}</div>
            <h3 style={{ color: '#667eea', margin: '8px 0', fontSize: 16 }}>{f.name}</h3>
            <p style={{ color: '#666', fontSize: 14, lineHeight: 1.6, margin: 0 }}>{f.desc}</p>
          </div>
        ))}
      </div>

      <hr className="divider" />

      <div style={{ textAlign: 'center', padding: '24px 16px', background: '#f8f9fa', borderRadius: 12, margin: '20px 0' }}>
        <h3 style={{ margin: '0 0 8px', color: '#333', fontSize: 18 }}>审核中</h3>
        <p style={{ color: '#666', fontSize: 15, margin: 0 }}>
          本工具正在 Temu Partner Platform 审核中<br />
          审核通过后将开放正式服务
        </p>
      </div>

      <hr className="divider" />

      <div style={{ maxWidth: 700, margin: '0 auto' }} id="faq">
        <h2 className="section-title">常见问题</h2>
        {[
          { q: '现在可以注册使用吗？', a: '可以注册体验基础功能，部分模块需 Temu API 审核通过后才可对接真实数据。' },
          { q: '收费吗？', a: '基础版注册后免费使用 30 天，后续定价待定。' },
          { q: '数据安全吗？', a: '传输全程 HTTPS 加密，凭证 AES-256 加密存储，按账号严格隔离。' },
        ].map((item, i) => (
          <div key={i} style={{ margin: '10px 0', padding: '14px 18px', background: '#f8f9fa', borderRadius: 8 }}>
            <div style={{ fontWeight: 'bold', fontSize: 15, marginBottom: 4, color: '#333' }}>{item.q}</div>
            <div style={{ color: '#555', fontSize: 14, lineHeight: 1.6 }}>{item.a}</div>
          </div>
        ))}
      </div>

      <div className="footer">
        <p style={{ margin: '4px 0', fontSize: 14 }}>© 2026 鲸云策 | Temu 卖家运营辅助工具</p>
        <p style={{ margin: '4px 0', fontSize: 13, color: '#888' }}>
          <a href="/terms" style={{ color: '#667eea', marginRight: 12 }}>用户服务协议</a>
          <a href="/privacy" style={{ color: '#667eea', marginRight: 12 }}>隐私政策</a>
          <a href="/login" style={{ color: '#667eea' }}>登录系统</a>
        </p>
        <p style={{ margin: '4px 0', fontSize: 12, color: '#aaa' }}>运营主体：个人开发者 · Temu Partner Platform Developer</p>
      </div>
    </div>
  );
}

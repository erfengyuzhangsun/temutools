import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

const { Title } = Typography;

export default function GuidePage() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: 24 }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(-1)}
          style={{ marginBottom: 16 }}
        >
          返回
        </Button>

        <div style={{
          background: '#fff',
          padding: '32px 40px',
          borderRadius: 12,
          boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
          lineHeight: 1.8,
          fontSize: 14,
          color: '#333',
        }}>
          <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>店铺绑定操作指南</Title>
          <p style={{ textAlign: 'center', color: '#999', marginBottom: 24, fontSize: 13 }}>
            全托管 / 半托管 / Y2 跨境店铺通用
          </p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            第 1 步：注册鲸云策
          </h2>
          <p>打开 <a href="https://www.jinpuhuang.com/login">www.jinpuhuang.com/login</a> 注册账号，勾选《用户服务协议》和《隐私政策》。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            第 2 步：在 Temu 授权「鲸云策」
          </h2>
          <p>用<strong>店铺主账号</strong>登录跨境卖家后台 → 开放平台 → 客户端管理 → 授权「鲸云策」→ 复制 <strong>Access Token</strong>。</p>
          <p>美国站入口：<a href="https://agentseller.temu.com/open-platform/system-manage/client-manage" target="_blank" rel="noreferrer">agentseller.temu.com</a></p>
          <p>欧洲站入口：<a href="https://agentseller-eu.temu.com/open-platform/system-manage/client-manage" target="_blank" rel="noreferrer">agentseller-eu.temu.com</a></p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            第 3 步：在鲸云策绑定店铺
          </h2>
          <p>登录后进入 <strong>API 同步</strong> → <strong>绑定店铺</strong> → 填写店铺名称、粘贴 Token、选择区域（美国/欧洲/全球）→ 勾选授权声明 → 保存。</p>
          <p>绑定成功后点击 <strong>同步订单</strong> 验证是否正常。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            常见问题
          </h2>
          <p><strong>全托管 / 半托管 / Y2 绑法一样吗？</strong> 一样，每个店铺各授权、各绑定一次。</p>
          <p><strong>Token 多久过期？</strong> 约 3 个月，过期后需在 Temu 重新授权并更新绑店。</p>
          <p><strong>找不到「鲸云策」？</strong> 请联系客服微信 <strong>returnHuangMuNing</strong>。</p>

          <hr style={{ margin: '20px 0', border: 'none', borderTop: '1px solid #eee' }} />

          <p style={{ textAlign: 'center', color: '#666' }}>
            详见 <a href="/terms">用户服务协议</a> 与 <a href="/privacy">隐私政策</a>
          </p>
        </div>
      </div>
    </div>
  );
}

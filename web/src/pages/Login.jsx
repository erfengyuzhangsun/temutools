import React, { useState } from 'react';
import { Form, Input, Button, Card, Tabs, Typography, Space, Checkbox, Divider, App } from 'antd';
import { MailOutlined, LockOutlined, RobotOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../api/client';

const { Title, Text, Paragraph } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [agreePrivacy, setAgreePrivacy] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);
  const policyVersion = '2026-05-18';
  const navigate = useNavigate();
  const { message } = App.useApp();

  const handleLogin = async (values) => {
    if (!agreePrivacy || !agreeTerms) {
      message.warning('请先阅读并同意《用户服务协议》和《隐私政策》');
      return;
    }
    setLoading(true);
    try {
      const resp = await login(values.email, values.password);
      localStorage.setItem('token', resp.data.token);
      localStorage.setItem('user', JSON.stringify(resp.data.user));
      localStorage.setItem('expiry', JSON.stringify(resp.data.expiry || {}));
      message.success('登录成功');
      navigate('/dashboard');
    } catch (err) {
      message.error(err?.error?.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values) => {
    if (!agreePrivacy || !agreeTerms) {
      message.warning('请先阅读并同意《用户服务协议》和《隐私政策》');
      return;
    }
    setLoading(true);
    try {
      const resp = await register(values.email, values.password, {
        agreed_terms: true,
        agreed_privacy: true,
        policy_version: policyVersion,
      });
      localStorage.setItem('token', resp.data.token);
      localStorage.setItem('user', JSON.stringify(resp.data.user));
      localStorage.setItem('expiry', JSON.stringify(resp.data.expiry || {}));
      message.success('注册成功');
      navigate('/dashboard');
    } catch (err) {
      if (err?.error?.code === 'CONFLICT') {
        message.error('该邮箱已注册，请直接登录');
      } else {
        message.error(err?.error?.message || '注册失败');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: 24,
    }}>
      <Card style={{ width: 420, borderRadius: 16, boxShadow: '0 8px 32px rgba(0,0,0,0.15)' }}>
        <Space direction="vertical" style={{ width: '100%', textAlign: 'center', marginBottom: 24 }}>
          <RobotOutlined style={{ fontSize: 48, color: '#667eea' }} />
          <Title level={3} style={{ margin: 0 }}>🐋 鲸云策</Title>
          <Text type="secondary">请输入邮箱和密码，开启您的运营管理之旅</Text>
        </Space>

        <Tabs centered items={[
          {
            key: 'login',
            label: '登录',
            children: (
              <Form onFinish={handleLogin} layout="vertical" size="large">
                <Form.Item name="email" rules={[{ required: true, type: 'email', message: '请输入有效邮箱' }]}>
                  <Input prefix={<MailOutlined />} placeholder="邮箱地址" autoComplete="email" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
                  <Input.Password prefix={<LockOutlined />} placeholder="密码" autoComplete="current-password" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block style={{ borderRadius: 8 }}>
                    登录
                  </Button>
                </Form.Item>
              </Form>
            ),
          },
          {
            key: 'register',
            label: '注册',
            children: (
              <Form onFinish={handleRegister} layout="vertical" size="large">
                <Form.Item name="email" rules={[{ required: true, type: 'email', message: '请输入有效邮箱' }]}>
                  <Input prefix={<MailOutlined />} placeholder="邮箱地址" autoComplete="email" />
                </Form.Item>
                <Form.Item name="password" rules={[
                  { required: true, min: 6, message: '密码至少6位' },
                ]}>
                  <Input.Password prefix={<LockOutlined />} placeholder="密码（至少6位）" autoComplete="new-password" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block style={{ borderRadius: 8 }}>
                    注册
                  </Button>
                </Form.Item>
              </Form>
            ),
          },
        ]} />

        <Checkbox checked={agreeTerms} onChange={(e) => setAgreeTerms(e.target.checked)} style={{ marginBottom: 4, display: 'flex' }}>
          <span>我已阅读并同意<a href="/terms" target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>《用户服务协议》</a></span>
        </Checkbox>
        <Checkbox checked={agreePrivacy} onChange={(e) => setAgreePrivacy(e.target.checked)} style={{ marginBottom: 8, display: 'flex' }}>
          <span>我已阅读并同意<a href="/privacy" target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()}>《隐私政策》</a></span>
        </Checkbox>

        <Divider />
        <Paragraph style={{ textAlign: 'center', margin: 0, color: '#999', fontSize: 13 }}>
          还没有访问密码？请联系微信：<Text strong>returnHuangMuNing</Text>
        </Paragraph>
      </Card>
    </div>
  );
}

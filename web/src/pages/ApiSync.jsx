import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Tag, Spin, message, Typography, Row, Modal, Input, Select, Alert } from 'antd';
import { CloudSyncOutlined, PlusOutlined, DeleteOutlined, LinkOutlined, CopyOutlined, SafetyOutlined } from '@ant-design/icons';
import { getApiSyncShops, bindShop, syncOrders, getTemuAuthUrl } from '../api/client';

const { Title } = Typography;

export default function ApiSyncPage() {
  const [shops, setShops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bindModal, setBindModal] = useState(false);
  const [shopName, setShopName] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [region, setRegion] = useState('us');
  const [appKey, setAppKey] = useState('');
  const [appSecret, setAppSecret] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [syncing, setSyncing] = useState(null);
  const [authUrl, setAuthUrl] = useState('');
  const [authModal, setAuthModal] = useState(false);
  const [authShopName, setAuthShopName] = useState('');
  const [generating, setGenerating] = useState(false);

  const fetchShops = () => {
    setLoading(true);
    getApiSyncShops().then((r) => setShops(r.data?.shops || [])).catch(() => setShops([])).finally(() => setLoading(false));
  };

  useEffect(() => { fetchShops(); }, []);

  const handleBind = async () => {
    if (!shopName || !accessToken) { message.warning('请填写店铺名称和Access Token'); return; }
    try {
      await bindShop(shopName, accessToken, region, appKey, appSecret);
      message.success('店铺绑定成功');
      setBindModal(false);
      setShopName('');
      setAccessToken('');
      setRegion('us');
      setAppKey('');
      setAppSecret('');
      setShowAdvanced(false);
      fetchShops();
    } catch (err) {
      message.error(err?.error?.message || '绑定失败');
    }
  };

  const handleAuthUrl = async () => {
    if (!authShopName) { message.warning('请填写店铺名称'); return; }
    setGenerating(true);
    try {
      const res = await getTemuAuthUrl(authShopName);
      setAuthUrl(res.data.auth_url);
    } catch (err) {
      message.error('生成授权链接失败：' + (err.response?.data?.message || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const copyAuthUrl = () => {
    navigator.clipboard.writeText(authUrl).then(() => {
      message.success('授权链接已复制');
    }).catch(() => {
      message.warning('复制失败，请手动选中复制');
    });
  };

  const handleSync = async (id) => {
    setSyncing(id);
    try {
      const r = await syncOrders(id);
      message.success(r.data?.message || '同步成功');
    } catch (err) {
      message.error('同步失败');
    } finally { setSyncing(null); }
  };

  const columns = [
    { title: '店铺ID', dataIndex: 'shop_id', key: 'shop_id' },
    { title: '店铺名称', dataIndex: 'shop_name', key: 'shop_name' },
    { title: '区域', dataIndex: 'region', key: 'region', render: (v) => {
      const labels = { us: '美国', global: '全球', eu: '欧洲', pa: '合作伙伴' };
      return <Tag>{labels[v] || v || '美国'}</Tag>;
    }},
    { title: '主营类目', dataIndex: 'main_category', key: 'main_category' },
    { title: '操作', key: 'action', render: (_, r) => (
      <Space>
        <Button size="small" icon={<CloudSyncOutlined />} loading={syncing === r.shop_id} onClick={() => handleSync(r.shop_id)}>同步订单</Button>
      </Space>
    )},
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={4}><CloudSyncOutlined /> API同步管理</Title>
        <Space>
          <Button icon={<SafetyOutlined />} onClick={() => setAuthModal(true)}>一键授权</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setBindModal(true)}>绑定店铺</Button>
        </Space>
      </Row>
      <Alert
        message="客户如何绑定店铺？"
        description="点击「一键授权」生成授权链接发给客户，客户在Temu卖家中心点击授权后自动完成绑定。也可以手动「绑定店铺」输入Access Token。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      <Card>
        <Table dataSource={shops} columns={columns} rowKey="shop_id" pagination={false} />
      </Card>
      <Modal title="绑定店铺" open={bindModal} onOk={handleBind} onCancel={() => setBindModal(false)} width={500}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input value={shopName} onChange={(e) => setShopName(e.target.value)} placeholder="店铺名称" />
          <Input value={accessToken} onChange={(e) => setAccessToken(e.target.value)} placeholder="Access Token" />
          <Select value={region} onChange={setRegion} style={{ width: '100%' }}
            options={[
              { value: 'us', label: '🇺🇸 美国 (us)' },
              { value: 'global', label: '🌐 全球 (global)' },
              { value: 'eu', label: '🇪🇺 欧洲 (eu)' },
            ]}
          />
          <Button type="link" size="small" onClick={() => setShowAdvanced(!showAdvanced)} style={{ padding: 0 }}>
            {showAdvanced ? '收起' : '展开'}高级设置（自定义 App Key/Secret）
          </Button>
          {showAdvanced && (
            <>
              <Input value={appKey} onChange={(e) => setAppKey(e.target.value)} placeholder="App Key（选填，留空使用系统默认）" />
              <Input.Password value={appSecret} onChange={(e) => setAppSecret(e.target.value)} placeholder="App Secret（选填，留空使用系统默认）" />
            </>
          )}
        </Space>
      </Modal>
      <Modal title="一键授权 — 生成授权链接" open={authModal} onCancel={() => { setAuthModal(false); setAuthUrl(''); }} footer={null} width={600}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <p style={{ margin: 0, color: '#666', fontSize: 14 }}>
            生成一个 Temu 授权链接，发给您的客户。客户点击链接后在 Temu 卖家中心授权，系统会自动完成店铺绑定。
          </p>
          <Input value={authShopName} onChange={(e) => setAuthShopName(e.target.value)} placeholder="给店铺取个名称（如：张三优选）" />
          <Button type="primary" onClick={handleAuthUrl} loading={generating} block>
            生成授权链接
          </Button>
          {authUrl && (
            <div style={{ background: '#f6f8fa', border: '1px solid #e8e8e8', borderRadius: 6, padding: 12 }}>
              <div style={{ fontSize: 13, color: '#333', wordBreak: 'break-all', marginBottom: 8, lineHeight: 1.6 }}>
                {authUrl}
              </div>
              <Button icon={<CopyOutlined />} onClick={copyAuthUrl} size="small">复制链接</Button>
            </div>
          )}
        </Space>
      </Modal>
    </div>
  );
}

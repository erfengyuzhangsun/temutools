import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Tag, Spin, message, Typography, Row, Modal, Input, InputNumber, Select } from 'antd';
import { CloudSyncOutlined, PlusOutlined, DeleteOutlined, LinkOutlined } from '@ant-design/icons';
import { getApiSyncShops, bindShop, syncOrders } from '../api/client';

const { Title } = Typography;

export default function ApiSyncPage() {
  const [shops, setShops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bindModal, setBindModal] = useState(false);
  const [shopName, setShopName] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [region, setRegion] = useState('us');
  const [syncing, setSyncing] = useState(null);

  const fetchShops = () => {
    setLoading(true);
    getApiSyncShops().then((r) => setShops(r.data?.shops || [])).catch(() => setShops([])).finally(() => setLoading(false));
  };

  useEffect(() => { fetchShops(); }, []);

  const handleBind = async () => {
    if (!shopName || !accessToken) { message.warning('请填写店铺名称和Access Token'); return; }
    try {
      await bindShop(shopName, accessToken, region);
      message.success('店铺绑定成功');
      setBindModal(false);
      setShopName('');
      setAccessToken('');
      setRegion('us');
      fetchShops();
    } catch (err) {
      message.error(err?.error?.message || '绑定失败');
    }
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
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setBindModal(true)}>绑定店铺</Button>
      </Row>
      <Card>
        <Table dataSource={shops} columns={columns} rowKey="shop_id" pagination={false} />
      </Card>
      <Modal title="绑定店铺" open={bindModal} onOk={handleBind} onCancel={() => setBindModal(false)}>
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
        </Space>
      </Modal>
    </div>
  );
}

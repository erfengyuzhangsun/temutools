import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Tag, Spin, message, Typography, Row, Col, Statistic, InputNumber } from 'antd';
import { SettingOutlined, ThunderboltOutlined, HistoryOutlined } from '@ant-design/icons';
import { getPricingLogs, autoHandlePricing } from '../api/client';

const { Title } = Typography;

export default function PricingPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [shopId, setShopId] = useState(1);
  const [handling, setHandling] = useState(false);

  const fetchLogs = () => {
    setLoading(true);
    getPricingLogs(shopId, 50).then((r) => setLogs(r.data?.logs || [])).catch(() => setLogs([])).finally(() => setLoading(false));
  };

  useEffect(() => { fetchLogs(); }, [shopId]);

  const handleAutoPricing = async () => {
    setHandling(true);
    try {
      const r = await autoHandlePricing(shopId);
      message.success(`核价处理完成，共 ${r.data?.handled_count || 0} 条`);
      fetchLogs();
    } catch (err) {
      message.error('处理失败');
    } finally { setHandling(false); }
  };

  const columns = [
    { title: 'SKU', dataIndex: 'sku', key: 'sku' },
    { title: '操作', dataIndex: 'action', key: 'action', render: (v) => <Tag color={v === 'accept' ? 'green' : v === 'reject' ? 'red' : 'orange'}>{v === 'accept' ? '接受' : v === 'reject' ? '拒绝' : '跳过'}</Tag> },
    { title: '供货价', dataIndex: 'supply_price', key: 'supply_price', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '成本价', dataIndex: 'cost_price', key: 'cost_price', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '毛利率', dataIndex: 'gross_margin', key: 'gross_margin', render: (v) => <Tag color={v >= 20 ? 'green' : 'red'}>{v}%</Tag> },
    { title: '原因', dataIndex: 'reason', key: 'reason', ellipsis: true },
    { title: '活动', dataIndex: 'is_activity', key: 'is_activity', render: (v) => v ? <Tag color="blue">活动</Tag> : '-' },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={4}><SettingOutlined /> 核价管理</Title>
        <Space>
          <InputNumber min={1} value={shopId} onChange={setShopId} style={{ width: 120 }} placeholder="店铺ID" />
          <Button type="primary" icon={<ThunderboltOutlined />} onClick={handleAutoPricing} loading={handling}>自动核价</Button>
        </Space>
      </Row>
      <Card title={<span><HistoryOutlined /> 核价记录</span>}>
        <Table dataSource={logs} columns={columns} rowKey="log_id" pagination={{ pageSize: 20 }} size="small" />
      </Card>
    </div>
  );
}

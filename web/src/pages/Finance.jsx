import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Spin, Typography, Descriptions, Tag, Button, Table, Select, Space, message, Tabs } from 'antd';
import { DollarOutlined, RiseOutlined, FallOutlined, HistoryOutlined, SyncOutlined, FileTextOutlined } from '@ant-design/icons';
import { getFinanceMonthly, getFinanceForecast } from '../api/client';
import api from '../api/client';

const { Title, Text } = Typography;

export default function FinancePage() {
  const [summary, setSummary] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [shops, setShops] = useState([]);
  const [shopID, setShopID] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [records, setRecords] = useState([]);
  const [recordsLoading, setRecordsLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      getFinanceMonthly().catch(() => ({ data: { summary: {} } })),
      getFinanceForecast().catch(() => ({ data: { forecast: {} } })),
    ]).then(([m, f]) => {
      setSummary(m.data?.summary || {});
      setForecast(f.data?.forecast || {});
    }).finally(() => setLoading(false));

    api.get('/api-sync/shops').then(r => {
      if (r?.success) setShops(r.data?.shops || []);
    });
  }, []);

  const syncSettlement = async () => {
    if (!shopID) { message.warning('请先选择店铺'); return; }
    setSyncing(true);
    try {
      const r = await api.post('/finance/sync-settlement', { shop_id: shopID });
      if (r?.success) {
        message.success(`同步成功: ${r.data?.message || ''}`);
        fetchHistory();
      } else {
        message.error(r?.message || '同步失败');
      }
    } catch (e) {
      message.error('同步请求失败');
    } finally {
      setSyncing(false);
    }
  };

  const fetchHistory = async () => {
    if (!shopID) return;
    setRecordsLoading(true);
    try {
      const r = await api.get(`/finance/history?shop_id=${shopID}&limit=100`);
      if (r?.success) {
        setRecords(r.data?.records || []);
      }
    } finally {
      setRecordsLoading(false);
    }
  };

  useEffect(() => {
    if (shopID) fetchHistory();
  }, [shopID]);

  const recordColumns = [
    { title: '订单号', dataIndex: 'order_sn', key: 'order_sn', width: 180 },
    { title: '结算金额', dataIndex: 'settlement_amount', key: 'settlement_amount', width: 110,
      render: (v) => `¥${(v || 0).toFixed(2)}`,
    },
    { title: '平台费用', dataIndex: 'platform_fee', key: 'platform_fee', width: 100,
      render: (v) => `¥${(v || 0).toFixed(2)}`,
    },
    { title: '总收入', dataIndex: 'total_amount', key: 'total_amount', width: 100,
      render: (v) => `¥${(v || 0).toFixed(2)}`,
    },
    { title: '利润率', dataIndex: 'profit_rate', key: 'profit_rate', width: 80,
      render: (v) => v ? `${(v * 100).toFixed(1)}%` : '-',
    },
    { title: '同步时间', dataIndex: 'created_at', key: 'created_at', width: 160,
      render: (v) => v ? new Date(v).toLocaleString() : '-',
    },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const settlementPanel = (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select placeholder="选择店铺" style={{ width: 250 }}
          value={shopID || undefined} onChange={setShopID}
          options={shops.map(s => ({ label: s.shop_name + (s.main_category ? ` (${s.main_category})` : ''), value: s.shop_id }))}
          allowClear onClear={() => setShopID(0)} />
        <Button type="primary" icon={<SyncOutlined />} onClick={syncSettlement} loading={syncing}>
          同步结算数据
        </Button>
        <Button icon={<FileTextOutlined />} onClick={fetchHistory} loading={recordsLoading}>
          刷新记录
        </Button>
      </Space>
      <Table dataSource={records} columns={recordColumns} rowKey={(r) => r.order_sn + (r.id || '')}
        loading={recordsLoading} size="small" pagination={{ pageSize: 20 }}
        scroll={{ x: 750 }} locale={{ emptyText: '请选择店铺并点击同步' }} />
    </div>
  );

  return (
    <div>
      <Title level={4}><DollarOutlined /> 财务结算</Title>

      <Tabs defaultActiveKey="overview" items={[
        {
          key: 'overview', label: '总览',
          children: (
            <>
              <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={6}><Card><Statistic title="总收入" value={summary.total_revenue || 0} prefix={<RiseOutlined />} precision={2} suffix="元" valueStyle={{ color: '#3f8600' }} /></Card></Col>
                <Col span={6}><Card><Statistic title="总利润" value={summary.total_profit || 0} prefix={<DollarOutlined />} precision={2} suffix="元" valueStyle={{ color: '#3f8600' }} /></Card></Col>
                <Col span={6}><Card><Statistic title="总费用" value={summary.total_fees || 0} prefix={<FallOutlined />} precision={2} suffix="元" valueStyle={{ color: '#cf1322' }} /></Card></Col>
                <Col span={6}><Card><Statistic title="店铺数" value={summary.shop_count || 0} prefix={<HistoryOutlined />} suffix="个" /></Card></Col>
              </Row>
              <Card title={`结算周期：${summary.month || '—'}`} style={{ marginBottom: 16 }}>
                <Descriptions column={2} bordered size="small">
                  <Descriptions.Item label="用户ID">{summary.user_id}</Descriptions.Item>
                  <Descriptions.Item label="店铺数">{summary.shop_count}</Descriptions.Item>
                  <Descriptions.Item label="总收入">¥{summary.total_revenue?.toFixed(2) || '0.00'}</Descriptions.Item>
                  <Descriptions.Item label="总利润">¥{summary.total_profit?.toFixed(2) || '0.00'}</Descriptions.Item>
                  <Descriptions.Item label="总费用">¥{summary.total_fees?.toFixed(2) || '0.00'}</Descriptions.Item>
                </Descriptions>
              </Card>
              {forecast && (
                <Card title="下月预测">
                  <Row gutter={16}>
                    <Col span={8}><Statistic title="预计收入" value={forecast.next_month_revenue || 0} precision={2} suffix="元" /></Col>
                    <Col span={8}><Statistic title="预计利润" value={forecast.next_month_profit || 0} precision={2} suffix="元" /></Col>
                    <Col span={8}><Statistic title="置信度" value={forecast.confidence === 'high' ? '高' : forecast.confidence === 'low' ? '低' : '中'} suffix={<Tag color="blue">{forecast.confidence}</Tag>} /></Col>
                  </Row>
                  <p style={{ marginTop: 16, color: '#999' }}>{forecast.message}</p>
                </Card>
              )}
            </>
          ),
        },
        {
          key: 'settlement', label: '结算记录',
          children: settlementPanel,
        },
      ]} />
    </div>
  );
}

import React, { useState, useEffect, useMemo } from 'react';
import { Row, Col, Card, Statistic, Table, Spin, Alert, Tag, Typography, Button } from 'antd';
import {
  DollarOutlined, ShoppingCartOutlined, WarningOutlined,
  RiseOutlined, FallOutlined, AlertOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getDashboardOverview, getDashboardAlerts } from '../api/client';

const { Title } = Typography;

export default function DashboardPage() {
  const [overview, setOverview] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const expiry = useMemo(() => {
    const raw = localStorage.getItem('expiry');
    return raw ? JSON.parse(raw) : {};
  }, []);

  useEffect(() => {
    Promise.all([
      getDashboardOverview().catch(() => ({ data: {} })),
      getDashboardAlerts().catch(() => ({ data: { alerts: [] } })),
    ]).then(([overviewResp, alertsResp]) => {
      setOverview(overviewResp.data || {});
      setAlerts(alertsResp.data?.alerts || []);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const severityColor = { high: 'red', medium: 'orange', low: 'blue' };
  const columns = [
    { title: '店铺', dataIndex: 'shop_name', key: 'shop_name' },
    { title: '利润', dataIndex: 'profit', key: 'profit', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '收入', dataIndex: 'revenue', key: 'revenue', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '核价待处理', dataIndex: 'pricing_pending', key: 'pricing_pending', render: (v) => v > 0 ? <Tag color="orange">{v}</Tag> : v },
    { title: '库存告警', dataIndex: 'inventory_alerts', key: 'inventory_alerts', render: (v) => v > 0 ? <Tag color="red">{v}</Tag> : v },
    { title: '风控告警', dataIndex: 'risk_warnings', key: 'risk_warnings', render: (v) => v > 0 ? <Tag color="red">{v}</Tag> : v },
  ];

  const alertColumns = [
    { title: '店铺', dataIndex: 'shop', key: 'shop' },
    { title: '类型', dataIndex: 'type', key: 'type', render: (v) => <Tag>{v}</Tag> },
    { title: '内容', dataIndex: 'msg', key: 'msg', ellipsis: true },
    {
      title: '等级', dataIndex: 'severity', key: 'severity',
      render: (v) => <Tag color={severityColor[v]}>{v === 'high' ? '高危' : v === 'medium' ? '中危' : '低危'}</Tag>,
    },
  ];

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>数据看板</Title>

      {expiry.is_expired && (
        <Alert
          message="套餐已过期"
          description="您的套餐已过期，部分功能可能受限。请联系客服续费。"
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          action={
            <Button size="small" danger onClick={() => navigate('/admin')}>
              联系客服
            </Button>
          }
        />
      )}

      {expiry.is_expiring_soon && !expiry.is_expired && (
        <Alert
          message={`套餐即将到期（剩余 ${expiry.days_remaining} 天）`}
          description={`您的套餐将在 ${expiry.days_remaining} 天后到期，请及时联系客服续费以免影响使用。`}
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="总利润" value={overview.total_profit || 0} prefix={<RiseOutlined />} precision={2} suffix="元" valueStyle={{ color: '#3f8600' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="总收入" value={overview.total_revenue || 0} prefix={<DollarOutlined />} precision={2} suffix="元" /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="店铺数" value={overview.shop_count || 0} prefix={<ShoppingCartOutlined />} suffix="个" /></Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="告警总数"
              value={overview.total_alerts || 0}
              prefix={<WarningOutlined />}
              valueStyle={overview.total_alerts > 0 ? { color: '#cf1322' } : { color: '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      {alerts.length > 0 && (
        <Card title={<span><AlertOutlined /> 实时告警</span>} style={{ marginBottom: 24 }}>
          <Table dataSource={alerts} columns={alertColumns} rowKey={(_, i) => i} pagination={false} size="small" />
        </Card>
      )}

      <Card title="店铺详情">
        <Table
          dataSource={overview.shop_details || []}
          columns={columns}
          rowKey="shop_id"
          pagination={false}
          size="middle"
        />
      </Card>
    </div>
  );
}

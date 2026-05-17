import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Spin, Typography, Descriptions, Tag } from 'antd';
import { DollarOutlined, RiseOutlined, FallOutlined, HistoryOutlined } from '@ant-design/icons';
import { getFinanceMonthly, getFinanceForecast } from '../api/client';

const { Title, Text } = Typography;

export default function FinancePage() {
  const [summary, setSummary] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getFinanceMonthly().catch(() => ({ data: { summary: {} } })),
      getFinanceForecast().catch(() => ({ data: { forecast: {} } })),
    ]).then(([m, f]) => {
      setSummary(m.data?.summary || {});
      setForecast(f.data?.forecast || {});
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Title level={4}><DollarOutlined /> 财务结算</Title>
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
    </div>
  );
}

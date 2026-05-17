import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Spin, Typography, Tag } from 'antd';
import { BarChartOutlined, RiseOutlined, DollarOutlined, ShopOutlined } from '@ant-design/icons';
import { getAnalysisReport } from '../api/client';

const { Title } = Typography;

export default function AnalysisPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalysisReport().then((r) => setReport(r.data?.report || null)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!report) return <Card><div style={{ textAlign: 'center', padding: 60, color: '#999' }}>暂无数据</div></Card>;

  const columns = [
    { title: '店铺', dataIndex: 'shop_name', key: 'shop_name' },
    { title: '利润', dataIndex: 'profit', key: 'profit', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '收入', dataIndex: 'revenue', key: 'revenue', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '利润率', dataIndex: 'profit_rate', key: 'profit_rate', render: (v) => <Tag color={v < 0 ? 'red' : 'green'}>{v}%</Tag> },
  ];

  return (
    <div>
      <Title level={4}><BarChartOutlined /> 数据分析报告</Title>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}><Card><Statistic title="总利润" value={report.summary?.total_profit || 0} prefix={<RiseOutlined />} precision={2} suffix="元" valueStyle={{ color: '#3f8600' }} /></Card></Col>
        <Col span={8}><Card><Statistic title="总收入" value={report.summary?.total_revenue || 0} prefix={<DollarOutlined />} precision={2} suffix="元" /></Card></Col>
        <Col span={8}><Card><Statistic title="店铺数" value={report.total_shops || 0} prefix={<ShopOutlined />} suffix="个" /></Card></Col>
      </Row>
      <Card title={`分析周期：${report.period}`}>
        <Table dataSource={report.shop_reports || []} columns={columns} rowKey="shop_id" pagination={false} />
      </Card>
    </div>
  );
}

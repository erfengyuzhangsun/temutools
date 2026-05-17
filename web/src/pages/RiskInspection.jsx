import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Spin, Typography, Descriptions, Tag, Progress, Table, Button } from 'antd';
import { SafetyOutlined, CheckCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { getRiskReport } from '../api/client';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

export default function RiskInspectionPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getRiskReport().then((r) => setReport(r.data?.report || null)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!report) return <Card><div style={{ textAlign: 'center', padding: 60, color: '#999' }}>暂无报告</div></Card>;

  const alertColumns = [
    { title: '店铺', dataIndex: 'shop_name', key: 'shop_name' },
    { title: '类型', dataIndex: 'type', key: 'type', render: (v) => <Tag>{v}</Tag> },
    { title: '内容', dataIndex: 'message', key: 'message' },
    { title: '等级', dataIndex: 'severity', key: 'severity', render: (v) => <Tag color={v === 'high' ? 'red' : v === 'medium' ? 'orange' : 'blue'}>{v}</Tag> },
  ];

  const riskColor = report.risk_level === 'high' ? '#cf1322' : report.risk_level === 'medium' ? '#faad14' : '#3f8600';

  return (
    <div>
      <Title level={4}><SafetyOutlined /> 风控体检报告</Title>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}><Card><Statistic title="综合评分" value={report.overall_score} prefix={<SafetyOutlined />} suffix="分" valueStyle={{ color: riskColor }} /></Card></Col>
        <Col span={6}><Card><Statistic title="风险等级" value={report.risk_level === 'high' ? '高危' : report.risk_level === 'medium' ? '中危' : '低危'} prefix={<WarningOutlined />} valueStyle={{ color: riskColor }} /></Card></Col>
        <Col span={6}><Card><Statistic title="店铺数" value={report.shop_count} suffix="个" /></Card></Col>
        <Col span={6}><Card><Statistic title="告警数" value={report.alerts?.length || 0} prefix={<WarningOutlined />} valueStyle={{ color: report.alerts?.length > 0 ? '#cf1322' : '#3f8600' }} /></Card></Col>
      </Row>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card><Progress percent={report.overall_score} strokeColor={riskColor} format={(p) => `${p}分`} /></Card>
        </Col>
      </Row>
      {report.alerts?.length > 0 && (
        <Card title="当前告警" style={{ marginBottom: 16 }}>
          <Table dataSource={report.alerts} columns={alertColumns} rowKey={(_, i) => i} pagination={false} size="small" />
        </Card>
      )}
      <Card title="摘要信息">
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="用户ID">{report.user_id}</Descriptions.Item>
          <Descriptions.Item label="检查时间">{report.checked_at}</Descriptions.Item>
          <Descriptions.Item label="综合评分">{report.overall_score}</Descriptions.Item>
          <Descriptions.Item label="风险等级"><Tag color={riskColor}>{report.risk_level}</Tag></Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
}

import React, { useState } from 'react';
import { Card, Button, Typography, message, Table, Tag, Space, Row, Col, Statistic } from 'antd';
import { SafetyOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { runRiskGuardCheck } from '../api/client';
const { Title } = Typography;

export default function RiskGuardPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    setLoading(true);
    try {
      const r = await runRiskGuardCheck();
      setResult(r.data);
      message.success('检查完成');
    } catch (err) { message.error('检查失败'); } finally { setLoading(false); }
  };

  return (
    <div>
      <Title level={4}><SafetyOutlined /> 风控引擎</Title>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={24}><Button type="primary" icon={<SafetyOutlined />} onClick={handleCheck} loading={loading} size="large">执行风控检查</Button></Col>
      </Row>
      {result && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={24}><Card><Statistic title="检查结果" value={result.passed ? '通过 ✓' : '未通过 ✗'} prefix={result.passed ? <CheckCircleOutlined /> : <CloseCircleOutlined />} valueStyle={{ color: result.passed ? '#3f8600' : '#cf1322' }} /></Card></Col>
        </Row>
      )}
      {result?.checks?.length > 0 && (
        <Card title="检查项">
          <Table dataSource={result.checks} rowKey="name"
            columns={[
              { title: '检查项', dataIndex: 'name', key: 'name' },
              { title: '结果', dataIndex: 'passed', key: 'passed', render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? '通过' : '未通过'}</Tag> },
            ]} pagination={false} />
        </Card>
      )}
    </div>
  );
}

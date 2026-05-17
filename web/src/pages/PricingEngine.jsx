import React, { useState } from 'react';
import { Card, InputNumber, Button, Row, Col, Statistic, Typography, Divider, message, Space, Table } from 'antd';
import { ExperimentOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { calculatePrice, batchCalculate } from '../api/client';

const { Title, Text } = Typography;

export default function PricingEnginePage() {
  const [costPrice, setCostPrice] = useState(50);
  const [margin, setMargin] = useState(20);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [batchItems, setBatchItems] = useState([
    { cost_price: 30, expected_margin: 15 },
    { cost_price: 50, expected_margin: 20 },
    { cost_price: 100, expected_margin: 25 },
  ]);
  const [batchResults, setBatchResults] = useState([]);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const r = await calculatePrice(costPrice, margin);
      setResult(r.data?.result);
    } catch (err) { message.error('计算失败'); } finally { setLoading(false); }
  };

  const handleBatch = async () => {
    try {
      const r = await batchCalculate(batchItems);
      setBatchResults(r.data?.results || []);
      message.success('批量计算完成');
    } catch (err) { message.error('批量计算失败'); }
  };

  const singlePrice = costPrice / (1 - margin / 100);

  return (
    <div>
      <Title level={4}><ExperimentOutlined /> 核价引擎</Title>
      <Row gutter={16}>
        <Col span={12}>
          <Card title="单次核价">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>成本价：</Text>
              <InputNumber value={costPrice} onChange={setCostPrice} prefix="¥" style={{ width: '100%' }} min={0} />
              <Text>期望毛利率：</Text>
              <InputNumber value={margin} onChange={setMargin} suffix="%" style={{ width: '100%' }} min={0} max={100} />
              <Button type="primary" icon={<ThunderboltOutlined />} onClick={handleCalculate} loading={loading} block>计算供货价</Button>
            </Space>
            {result && (
              <>
                <Divider />
                <Row gutter={8}>
                  <Col span={8}><Statistic title="成本价" value={result.cost_price} prefix="¥" precision={2} /></Col>
                  <Col span={8}><Statistic title="期望毛利率" value={result.expected_margin} suffix="%" /></Col>
                  <Col span={8}><Statistic title="建议供货价" value={parseFloat(result.recommended_price)} prefix="¥" precision={2} valueStyle={{ color: '#3f8600', fontWeight: 'bold', fontSize: 24 }} /></Col>
                </Row>
              </>
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="批量核价">
            <Button onClick={handleBatch} type="primary" style={{ marginBottom: 16 }}>批量计算</Button>
            <Table dataSource={batchResults.length > 0 ? batchResults : batchItems.map((item, i) => ({ ...item, key: i, recommended_price: item.cost_price / (1 - item.expected_margin / 100) }))}
              columns={[
                { title: '成本价', dataIndex: 'cost_price', key: 'cost_price', render: (v) => `¥${v?.toFixed(2)}` },
                { title: '毛利率', dataIndex: 'expected_margin', key: 'expected_margin', render: (v) => `${v}%` },
                { title: '建议供货价', dataIndex: 'recommended_price', key: 'recommended_price', render: (v) => <Text strong style={{ color: '#3f8600' }}>¥{parseFloat(v).toFixed(2)}</Text> },
              ]}
              pagination={false} size="small" />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

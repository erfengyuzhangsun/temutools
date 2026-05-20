import React, { useState, useEffect } from 'react';
import { Card, Table, InputNumber, Select, Button, Statistic, Row, Col, Space, message, Tag } from 'antd';
import { SwapOutlined, ReloadOutlined } from '@ant-design/icons';
import api from '../api/client';

export default function Exchange() {
  const [rates, setRates] = useState([]);
  const [base, setBase] = useState('USD');
  const [loading, setLoading] = useState(false);
  const [from, setFrom] = useState('USD');
  const [to, setTo] = useState('CNY');
  const [amount, setAmount] = useState(100);
  const [result, setResult] = useState(null);
  const [currencies, setCurrencies] = useState([]);

  useEffect(() => {
    api.get('/exchange/currencies').then(r => {
      if (r.data?.success) {
        const list = r.data.data?.currencies || [];
        setCurrencies(list);
      }
    });
  }, []);

  const fetchRates = async (b) => {
    setLoading(true);
    try {
      const r = await api.get(`/exchange/rates?base=${b || base}`);
      if (r.data?.success) {
        setRates(r.data.data?.rates || []);
        setBase(r.data.data?.base || b);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRates(base); }, []);

  const doConvert = async () => {
    if (!from || !to || amount <= 0) { message.warning('请填写完整信息'); return; }
    try {
      const r = await api.get(`/exchange/convert?from=${from}&to=${to}&amount=${amount}`);
      if (r.data?.success) {
        setResult(r.data.data?.conversion);
      }
    } catch {
      message.error('转换失败');
    }
  };

  const columns = [
    { title: '货币', dataIndex: 'code', key: 'code', width: 80,
      render: (v) => <Tag>{v}</Tag>,
    },
    { title: '名称', dataIndex: 'name', key: 'name', width: 120 },
    { title: `汇率 (1 ${base}=?)`, dataIndex: 'rate', key: 'rate', width: 150,
      render: (v) => v?.toFixed(4),
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="货币转换" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <Select showSearch value={from} onChange={setFrom} style={{ width: 120 }}
                  options={currencies.map(c => ({ label: c, value: c }))} />
                <SwapOutlined />
                <Select showSearch value={to} onChange={setTo} style={{ width: 120 }}
                  options={currencies.map(c => ({ label: c, value: c }))} />
              </Space>
              <Space>
                <InputNumber value={amount} onChange={setAmount} min={0.01}
                  style={{ width: 160 }} addonBefore="金额" precision={2} />
                <Button type="primary" icon={<SwapOutlined />} onClick={doConvert}>转换</Button>
              </Space>
              {result && (
                <Card size="small" style={{ background: '#f6ffed' }}>
                  <Statistic
                    title={`${result.amount} ${result.from}`}
                    value={result.result}
                    suffix={result.to}
                    precision={2}
                  />
                  <div style={{ color: '#999', fontSize: 12, marginTop: 4 }}>
                    汇率: 1 {result.from} = {result.rate} {result.to}
                  </div>
                </Card>
              )}
            </Space>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="汇率来源" size="small">
            <p>数据来源: <strong>open.er-api.com</strong>（免费）</p>
            <p>缓存策略: 每 1 小时自动刷新</p>
            <p>支持的币种: <Tag>{currencies.length}</Tag> 种</p>
          </Card>
        </Col>
      </Row>

      <Card title={`汇率表（基础货币: ${base}）`}
        extra={<Button icon={<ReloadOutlined />} onClick={() => fetchRates(base)} loading={loading}>刷新</Button>}>
        <Table dataSource={rates} columns={columns} rowKey="code" loading={loading}
          size="small" pagination={{ pageSize: 30 }} scroll={{ y: 400 }} />
      </Card>
    </div>
  );
}

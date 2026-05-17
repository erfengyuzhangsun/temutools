import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Spin, message, Typography, Row, Modal, Input, InputNumber, Statistic, Col, Checkbox } from 'antd';
import { PlusOutlined, ToolOutlined } from '@ant-design/icons';
import { getFactoryProducts, createFactoryProduct, getFactoryAnalysis } from '../api/client';

const { Title } = Typography;

export default function FactoryCostPage() {
  const [products, setProducts] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [createModal, setCreateModal] = useState(false);
  const [form, setForm] = useState({});

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      getFactoryProducts().catch(() => ({ data: { products: [] } })),
      getFactoryAnalysis().catch(() => ({ data: { analysis: null } })),
    ]).then(([p, a]) => {
      setProducts(p.data?.products || []);
      setAnalysis(a.data?.analysis || null);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleCreate = async () => {
    if (!form.productName || !form.skuCode) { message.warning('请填写产品名称和SKU'); return; }
    try {
      await createFactoryProduct(form);
      message.success('产品创建成功');
      setCreateModal(false);
      setForm({});
      fetchData();
    } catch (err) { message.error('创建失败'); }
  };

  const columns = [
    { title: '产品名称', dataIndex: 'product_name', key: 'product_name' },
    { title: 'SKU', dataIndex: 'sku_code', key: 'sku_code' },
    { title: '材料成本', dataIndex: 'material_cost', key: 'material_cost', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '总成本', dataIndex: 'total_cost', key: 'total_cost', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '建议供货价', dataIndex: 'suggested_supply_price', key: 'suggested_supply_price', render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '期望利润率', dataIndex: 'expected_profit_margin', key: 'expected_profit_margin', render: (v) => `${v}%` },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={4}><ToolOutlined /> 工厂成本管理</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModal(true)}>录入产品</Button>
      </Row>
      {analysis && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={8}><Card><Statistic title="产品总数" value={analysis.total_products || 0} suffix="个" /></Card></Col>
          <Col span={8}><Card><Statistic title="平均成本" value={analysis.avg_cost || 0} prefix="¥" precision={2} /></Card></Col>
          <Col span={8}><Card><Statistic title="平均利润率" value={analysis.avg_margin || 0} suffix="%" valueStyle={{ color: '#3f8600' }} /></Card></Col>
        </Row>
      )}
      <Card><Table dataSource={products} columns={columns} rowKey="product_id" pagination={false} /></Card>
      <Modal title="录入产品" open={createModal} onOk={handleCreate} onCancel={() => setCreateModal(false)} width={600}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Row gutter={8}><Col span={12}><Input value={form.productName} onChange={(e) => setForm({...form, productName: e.target.value})} placeholder="产品名称 *" /></Col><Col span={12}><Input value={form.skuCode} onChange={(e) => setForm({...form, skuCode: e.target.value})} placeholder="SKU编码 *" /></Col></Row>
          <Row gutter={8}><Col span={8}><InputNumber value={form.materialCost} onChange={(v) => setForm({...form, materialCost: v})} placeholder="材料成本" style={{ width: '100%' }} prefix="¥" /></Col><Col span={8}><InputNumber value={form.laborCost} onChange={(v) => setForm({...form, laborCost: v})} placeholder="人工成本" style={{ width: '100%' }} prefix="¥" /></Col><Col span={8}><InputNumber value={form.packagingCost} onChange={(v) => setForm({...form, packagingCost: v})} placeholder="包装成本" style={{ width: '100%' }} prefix="¥" /></Col></Row>
          <Row gutter={8}><Col span={12}><InputNumber value={form.shippingCost} onChange={(v) => setForm({...form, shippingCost: v})} placeholder="物流成本" style={{ width: '100%' }} prefix="¥" /></Col><Col span={12}><InputNumber value={form.otherCost} onChange={(v) => setForm({...form, otherCost: v})} placeholder="其他成本" style={{ width: '100%' }} prefix="¥" /></Col></Row>
          <Row gutter={8}><Col span={12}><InputNumber value={form.expectedProfitMargin} onChange={(v) => setForm({...form, expectedProfitMargin: v})} placeholder="期望利润率(%)" style={{ width: '100%' }} suffix="%" /></Col><Col span={12}><Checkbox checked={form.isFullCommission} onChange={(e) => setForm({...form, isFullCommission: e.target.checked})}>全托管</Checkbox></Col></Row>
        </Space>
      </Modal>
    </div>
  );
}

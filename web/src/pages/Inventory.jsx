import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Space, Tag, Spin, message, Typography, Row, Col, Statistic, Modal, InputNumber } from 'antd';
import { SyncOutlined, AlertOutlined, ShoppingCartOutlined } from '@ant-design/icons';
import { getInventoryList, syncInventory } from '../api/client';

const { Title } = Typography;

export default function InventoryPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncModal, setSyncModal] = useState(false);
  const [shopId, setShopId] = useState(0);

  const fetchData = () => {
    setLoading(true);
    getInventoryList().then((r) => setData(r.data?.items || [])).catch(() => setData([])).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleSync = async () => {
    if (!shopId) { message.warning('请选择店铺'); return; }
    await syncInventory(shopId);
    message.success('同步完成');
    setSyncModal(false);
    fetchData();
  };

  const columns = [
    { title: '店铺', dataIndex: 'shop_name', key: 'shop_name' },
    { title: 'SKU数量', dataIndex: 'sku_count', key: 'sku_count' },
    { title: '低库存', dataIndex: 'low_stock_count', key: 'low_stock_count', render: (v) => v > 0 ? <Tag color="red">{v}</Tag> : v },
    { title: 'SKU编码', dataIndex: ['items', 0, 'sku_code'], key: 'sku_code', render: (_, r) => r.items?.[0]?.sku_code || '-' },
    { title: '利润率', dataIndex: ['items', 0, 'profit_rate'], key: 'profit_rate', render: (v) => v ? `${v}%` : '-' },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={4}><ShoppingCartOutlined /> 库存管理</Title>
        <Space>
          <Button icon={<SyncOutlined />} onClick={() => setSyncModal(true)}>同步库存</Button>
          <Button onClick={fetchData}>刷新</Button>
        </Space>
      </Row>

      {data.length === 0 ? (
        <Card><div style={{ textAlign: 'center', padding: 60, color: '#999' }}>暂无数据，请先录入产品资料或同步库存</div></Card>
      ) : (
        <Table dataSource={data} columns={columns} rowKey="shop_id" pagination={false} expandable={{
          expandedRowRender: (record) => (
            <Table dataSource={record.items || []} rowKey="sku_code" size="small"
              columns={[
                { title: 'SKU', dataIndex: 'sku_code', key: 'sku_code' },
                { title: '名称', dataIndex: 'sku_name', key: 'sku_name' },
                { title: '成本价', dataIndex: 'cost_price', key: 'cost_price', render: (v) => `¥${v?.toFixed(2)}` },
                { title: '销量', dataIndex: 'total_sales', key: 'total_sales' },
                { title: '利润', dataIndex: 'total_profit', key: 'total_profit', render: (v) => `¥${v?.toFixed(2)}` },
                { title: '利润率', dataIndex: 'profit_rate', key: 'profit_rate', render: (v) => <Tag color={v < 0 ? 'red' : 'green'}>{v}%</Tag> },
                { title: '低库存', dataIndex: 'is_low_stock', key: 'is_low_stock', render: (v) => v ? <Tag color="red">是</Tag> : '否' },
              ]} />
          ),
        }} />
      )}

      <Modal title="同步库存" open={syncModal} onOk={handleSync} onCancel={() => setSyncModal(false)}>
        <p>选择要同步库存的店铺ID：</p>
        <InputNumber min={1} value={shopId} onChange={setShopId} style={{ width: '100%' }} placeholder="输入店铺ID" />
      </Modal>
    </div>
  );
}

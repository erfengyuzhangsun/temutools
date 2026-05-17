import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Spin, message, Typography, Row, Modal, Input, Statistic, Col } from 'antd';
import { PlusOutlined, TeamOutlined } from '@ant-design/icons';
import { getSuppliers, addSupplier } from '../api/client';

const { Title } = Typography;

export default function SupplierPage() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createModal, setCreateModal] = useState(false);
  const [form, setForm] = useState({});

  const fetchData = () => {
    setLoading(true);
    getSuppliers().then((r) => setSuppliers(r.data?.suppliers || [])).catch(() => setSuppliers([])).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleAdd = async () => {
    if (!form.name) { message.warning('供应商名称不能为空'); return; }
    try {
      await addSupplier(form);
      message.success('供应商添加成功');
      setCreateModal(false);
      setForm({});
      fetchData();
    } catch (err) { message.error('添加失败'); }
  };

  const columns = [
    { title: '供应商名称', dataIndex: 'name', key: 'name' },
    { title: '联系人', dataIndex: 'contact', key: 'contact' },
    { title: '电话', dataIndex: 'phone', key: 'phone' },
    { title: '主营类目', dataIndex: 'main_category', key: 'main_category' },
    { title: '评分', dataIndex: 'rating', key: 'rating' },
    { title: '状态', dataIndex: 'status', key: 'status' },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={4}><TeamOutlined /> 供应商管理</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModal(true)}>添加供应商</Button>
      </Row>
      <Card><Table dataSource={suppliers} columns={columns} rowKey="supplier_id" pagination={false} /></Card>
      <Modal title="添加供应商" open={createModal} onOk={handleAdd} onCancel={() => setCreateModal(false)}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} placeholder="供应商名称 *" />
          <Input value={form.contact} onChange={(e) => setForm({...form, contact: e.target.value})} placeholder="联系人" />
          <Input value={form.phone} onChange={(e) => setForm({...form, phone: e.target.value})} placeholder="电话" />
          <Input value={form.mainCategory} onChange={(e) => setForm({...form, mainCategory: e.target.value})} placeholder="主营类目" />
        </Space>
      </Modal>
    </div>
  );
}

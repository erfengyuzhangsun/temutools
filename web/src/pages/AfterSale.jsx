import React, { useState, useEffect } from 'react';
import { Card, Table, Tabs, Tag, Button, Modal, Descriptions, message, Select, Space } from 'antd';
import { SearchOutlined, EyeOutlined, SyncOutlined } from '@ant-design/icons';
import api from '../api/client';

const statusGroupMap = { 0: '全部', 1: '待处理', 2: '处理中', 3: '已完成', 5: '退款' };

export default function AfterSale() {
  const [shops, setShops] = useState([]);
  const [shopID, setShopID] = useState(0);
  const [aftersales, setAftersales] = useState([]);
  const [parentAftersales, setParentAftersales] = useState([]);
  const [loading, setLoading] = useState(false);
  const [returnModal, setReturnModal] = useState({ open: false, data: null, loading: false });

  useEffect(() => {
    api.get('/api-sync/shops').then(r => {
      if (r.data?.success) setShops(r.data.data?.shops || []);
    });
  }, []);

  const fetchAftersales = async () => {
    if (!shopID) { message.warning('请先选择店铺'); return; }
    setLoading(true);
    try {
      const [r1, r2] = await Promise.all([
        api.get(`/aftersale/list?shop_id=${shopID}&page=1&page_size=50`),
        api.get(`/aftersale/parent-list?shop_id=${shopID}&page=1&page_size=50`),
      ]);
      if (r1.data?.success) setAftersales(r1.data.data?.aftersales || []);
      if (r2.data?.success) setParentAftersales(r2.data.data?.parent_aftersales || []);
    } finally {
      setLoading(false);
    }
  };

  const viewReturnOrder = async (sn) => {
    setReturnModal({ open: true, data: null, loading: true });
    try {
      const r = await api.get(`/aftersale/parent-return-order?shop_id=${shopID}&parent_after_sales_sn=${sn}`);
      if (r.data?.success) {
        setReturnModal({ open: true, data: r.data.data?.return_order || r.data.data, loading: false });
      }
    } catch {
      setReturnModal({ open: true, data: null, loading: false });
    }
  };

  const aftersaleColumns = [
    { title: '售后单号', dataIndex: 'aftersale_id', key: 'aftersale_id', width: 160 },
    { title: '订单号', dataIndex: 'order_sn', key: 'order_sn', width: 180 },
    { title: '商品', dataIndex: 'goods_name', key: 'goods_name' },
    { title: 'SKU', dataIndex: 'sku', key: 'sku', width: 130 },
    { title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: (v) => <Tag color={v === 'COMPLETED' ? 'green' : v === 'APPROVED' ? 'blue' : v === 'REJECTED' ? 'red' : 'orange'}>{v || 'PENDING'}</Tag>,
    },
    { title: '原因', dataIndex: 'reason', key: 'reason', ellipsis: true },
    { title: '金额', dataIndex: 'amount', key: 'amount', width: 100, render: (v) => `¥${(v || 0).toFixed(2)}` },
    { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 60 },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 160 },
  ];

  const parentColumns = [
    { title: '父售后单号', dataIndex: 'parent_after_sales_sn', key: 'parent_after_sales_sn', width: 180 },
    { title: '父订单号', dataIndex: 'parent_order_sn', key: 'parent_order_sn', width: 180 },
    { title: '状态组', dataIndex: 'after_sales_status_group', key: 'after_sales_status_group', width: 100,
      render: (v) => <Tag>{statusGroupMap[v] || v}</Tag>,
    },
    { title: '售后状态', dataIndex: 'parent_after_sales_status', key: 'parent_after_sales_status', width: 100 },
    { title: '类型', dataIndex: 'after_sales_type', key: 'after_sales_type', width: 80,
      render: (v) => v === 1 ? '退货' : v === 2 ? '换货' : v === 3 ? '退款' : v,
    },
    { title: '创建时间', dataIndex: 'create_at', key: 'create_at', width: 160,
      render: (v) => v ? new Date(v * 1000).toLocaleString() : '-',
    },
    {
      title: '操作', key: 'action', width: 100,
      render: (_, r) => (
        <Button type="link" size="small" icon={<EyeOutlined />}
          onClick={() => viewReturnOrder(r.parent_after_sales_sn)}>
          退货详情
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Card title="售后管理" extra={
        <Space>
          <Select placeholder="选择店铺" style={{ width: 200 }}
            value={shopID || undefined} onChange={setShopID}
            options={shops.map(s => ({ label: s.shop_name + (s.main_category ? ` (${s.main_category})` : ''), value: s.shop_id }))}
            allowClear onClear={() => setShopID(0)} />
          <Button type="primary" icon={<SyncOutlined />} onClick={fetchAftersales} loading={loading}>查询</Button>
        </Space>
      }>
        <Tabs defaultActiveKey="aftersales" items={[
          {
            key: 'aftersales', label: `售后列表 (${aftersales.length})`,
            children: <Table dataSource={aftersales} columns={aftersaleColumns} rowKey="aftersale_id"
              loading={loading} size="small" pagination={{ pageSize: 20 }} scroll={{ x: 1100 }} />,
          },
          {
            key: 'parent', label: `父售后单 (${parentAftersales.length})`,
            children: <Table dataSource={parentAftersales} columns={parentColumns} rowKey="parent_after_sales_sn"
              loading={loading} size="small" pagination={{ pageSize: 20 }} scroll={{ x: 1000 }} />,
          },
        ]} />
      </Card>

      <Modal title="退货详情" open={returnModal.open} onCancel={() => setReturnModal({ open: false, data: null, loading: false })} footer={null} width={600}>
        {returnModal.loading ? <p>加载中...</p> : returnModal.data ? (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="父售后单号" span={2}>{returnModal.data.parent_after_sales_sn}</Descriptions.Item>
            <Descriptions.Item label="退货原因" span={2}>{returnModal.data.return_reason}</Descriptions.Item>
            <Descriptions.Item label="退货数量">{returnModal.data.return_quantity}</Descriptions.Item>
            <Descriptions.Item label="退货金额">¥{(returnModal.data.return_amount || 0).toFixed(2)}</Descriptions.Item>
            <Descriptions.Item label="退货状态" span={2}>
              <Tag color={returnModal.data.return_status === 'REFUNDED' ? 'green' : 'blue'}>{returnModal.data.return_status}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">{returnModal.data.create_at ? new Date(returnModal.data.create_at * 1000).toLocaleString() : '-'}</Descriptions.Item>
            <Descriptions.Item label="更新时间">{returnModal.data.update_at ? new Date(returnModal.data.update_at * 1000).toLocaleString() : '-'}</Descriptions.Item>
          </Descriptions>
        ) : <p>未找到退货详情</p>}
      </Modal>
    </div>
  );
}

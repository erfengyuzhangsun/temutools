import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Select, Space, message, Typography } from 'antd';
import { SyncOutlined, WarningOutlined } from '@ant-design/icons';
import api from '../api/client';

const { Title } = Typography;

const statusGroupMap = { 0: '全部', 1: '待处理', 2: '处理中', 3: '已完成', 5: '退款' };

export default function ReviewMonitor() {
  const [shops, setShops] = useState([]);
  const [shopID, setShopID] = useState(0);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get('/api-sync/shops').then(r => {
      if (r?.success) setShops(r.data?.shops || []);
    });
  }, []);

  const fetchReviews = async () => {
    if (!shopID) { message.warning('请先选择店铺'); return; }
    setLoading(true);
    try {
      const r = await api.get(`/review-monitor/reviews?shop_id=${shopID}&status_group=5&page_size=50`);
      if (r?.success) {
        setReviews(r.data?.reviews || []);
      }
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: '父售后单号', dataIndex: 'parent_after_sales_sn', key: 'parent_after_sales_sn', width: 180 },
    { title: '订单号', dataIndex: 'order_sn', key: 'order_sn', width: 180 },
    { title: '状态组', dataIndex: 'after_sales_status_group', key: 'after_sales_status_group', width: 90,
      render: (v) => <Tag color={v === 5 ? 'red' : 'blue'}>{statusGroupMap[v] || v}</Tag>,
    },
    { title: '售后状态', dataIndex: 'parent_after_sales_status', key: 'parent_after_sales_status', width: 100 },
    { title: '类型', dataIndex: 'after_sales_type', key: 'after_sales_type', width: 70,
      render: (v) => v === 1 ? '退货' : v === 2 ? '换货' : v === 3 ? '退款' : v,
    },
    { title: '创建时间', dataIndex: 'create_at', key: 'create_at', width: 160,
      render: (v) => v ? new Date(v * 1000).toLocaleString() : '-',
    },
    { title: '更新时间', dataIndex: 'update_at', key: 'update_at', width: 160,
      render: (v) => v ? new Date(v * 1000).toLocaleString() : '-',
    },
  ];

  return (
    <div>
      <Title level={4}><WarningOutlined /> 差评监控</Title>
      <Card extra={
        <Space>
          <Select placeholder="选择店铺" style={{ width: 200 }}
            value={shopID || undefined} onChange={setShopID}
            options={shops.map(s => ({ label: s.shop_name, value: s.shop_id }))}
            allowClear onClear={() => setShopID(0)} />
          <Button type="primary" icon={<SyncOutlined />} onClick={fetchReviews} loading={loading}>查询</Button>
        </Space>
      }>
        <p style={{ color: '#999', marginBottom: 16 }}>
          监控退款/售后订单（statusGroup=5），数据来源于售后API
        </p>
        <Table dataSource={reviews} columns={columns} rowKey="parent_after_sales_sn"
          loading={loading} size="small" pagination={{ pageSize: 20 }}
          scroll={{ x: 900 }} locale={{ emptyText: '请选择店铺并点击查询' }} />
      </Card>
    </div>
  );
}

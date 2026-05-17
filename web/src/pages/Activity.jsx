import React, { useState, useEffect } from 'react';
import { Card, Table, Typography, Spin, Tag } from 'antd';
import { GiftOutlined } from '@ant-design/icons';
import { getActivities } from '../api/client';
const { Title } = Typography;

export default function ActivityPage() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    getActivities().then((r) => setActivities(r.data?.activities || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);
  const columns = [
    { title: '活动名称', dataIndex: 'title', key: 'title' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (v) => <Tag>{v}</Tag> },
    { title: '开始时间', dataIndex: 'start_time', key: 'start_time' },
    { title: '结束时间', dataIndex: 'end_time', key: 'end_time' },
  ];
  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  return <div><Title level={4}><GiftOutlined /> 活动管理</Title><Card><Table dataSource={activities} columns={columns} rowKey={(_, i) => i} pagination={false} locale={{ emptyText: '暂无活动' }} /></Card></div>;
}

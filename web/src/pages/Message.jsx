import React, { useState, useEffect } from 'react';
import { Card, Table, Typography, Spin, Tag, Button, message, Space } from 'antd';
import { MessageOutlined } from '@ant-design/icons';
import { getMessages } from '../api/client';

const { Title, Text } = Typography;

export default function MessagePage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMessages().then((r) => setMessages(r.data?.messages || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title' },
    { title: '内容', dataIndex: 'content', key: 'content', ellipsis: true },
    { title: '状态', dataIndex: 'status', key: 'status', render: (v) => <Tag>{v || '未读'}</Tag> },
    { title: '时间', dataIndex: 'time', key: 'time' },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Title level={4}><MessageOutlined /> 消息售后</Title>
      <Card><Table dataSource={messages} columns={columns} rowKey={(_, i) => i} pagination={false} locale={{ emptyText: '暂无消息' }} /></Card>
    </div>
  );
}

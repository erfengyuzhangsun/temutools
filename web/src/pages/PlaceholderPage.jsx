import React from 'react';
import { Card, Typography, Empty } from 'antd';
import { SearchOutlined, AppstoreOutlined, FileTextOutlined } from '@ant-design/icons';
const { Title } = Typography;

export default function PlaceholderPage({ title, icon }) {
  return (
    <div>
      <Title level={4}>{icon} {title}</Title>
      <Card><Empty description={`「${title}」功能开发中，敬请期待`} /></Card>
    </div>
  );
}

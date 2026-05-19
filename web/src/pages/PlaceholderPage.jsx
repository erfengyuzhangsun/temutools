import React from 'react';
import { Card, Typography } from 'antd';
import { SearchOutlined, AppstoreOutlined, FileTextOutlined } from '@ant-design/icons';
const { Title, Paragraph } = Typography;

const moduleDescriptions = {
  '差评监控': {
    icon: <FileTextOutlined />,
    desc: '差评实时监控、自动告警、批量回复',
  },
  '批量操作': {
    icon: <AppstoreOutlined />,
    desc: '商品批量上下架、库存批量调整、价格批量修改',
  },
  '选品分析': {
    icon: <SearchOutlined />,
    desc: '市场趋势分析、竞品数据追踪、选品推荐',
  },
};

export default function PlaceholderPage({ title, icon }) {
  const info = moduleDescriptions[title] || { desc: '' };

  return (
    <div>
      <Title level={4}>{icon} {title}</Title>
      <Card>
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <div style={{ fontSize: 48, marginBottom: 16, opacity: 0.4 }}>
            {icon}
          </div>
          <Title level={5} type="secondary" style={{ marginBottom: 8 }}>
            「{title}」功能开发中
          </Title>
          {info.desc && (
            <Paragraph type="secondary" style={{ fontSize: 14, maxWidth: 400, margin: '0 auto' }}>
              预计功能：{info.desc}
            </Paragraph>
          )}
          <Paragraph type="secondary" style={{ fontSize: 13, marginTop: 12 }}>
            敬请期待后续更新
          </Paragraph>
        </div>
      </Card>
    </div>
  );
}

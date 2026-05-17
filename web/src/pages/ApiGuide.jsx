import React, { useState, useEffect } from 'react';
import { Card, Typography, Timeline, Steps, Spin } from 'antd';
import { ApiOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { getApiGuide } from '../api/client';
const { Title, Text, Paragraph } = Typography;

export default function ApiGuidePage() {
  const [guide, setGuide] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    getApiGuide().then((r) => setGuide(r.data?.guide || null)).catch(() => {}).finally(() => setLoading(false));
  }, []);
  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  return (
    <div>
      <Title level={4}><ApiOutlined /> API对接指引</Title>
      <Card>
        <Steps direction="vertical" current={-1} items={(guide?.steps || []).map((s) => ({
          title: s.title, description: s.url && <Text copyable>{s.url}</Text>,
        }))} />
        <Paragraph style={{ marginTop: 24, color: '#999' }}>
          完成以上步骤后，在"API同步"页面填入获取到的凭证即可正常使用。如无 API 凭证，系统将使用模拟数据。
        </Paragraph>
      </Card>
    </div>
  );
}

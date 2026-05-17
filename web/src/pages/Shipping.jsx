import React from 'react';
import { Card, Typography, Empty } from 'antd';
import { TruckOutlined } from '@ant-design/icons';

const { Title } = Typography;

export default function ShippingPage() {
  return <div><Title level={4}><TruckOutlined /> 物流发货</Title><Card><Empty description="暂无物流订单" /></Card></div>;
}

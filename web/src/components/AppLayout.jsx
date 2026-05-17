import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Typography, theme } from 'antd';
import {
  DashboardOutlined,
  DollarOutlined,
  ShoppingCartOutlined,
  BarChartOutlined,
  MessageOutlined,
  SettingOutlined,
  CloudSyncOutlined,
  ExperimentOutlined,
  SafetyOutlined,
  TeamOutlined,
  ToolOutlined,
  SearchOutlined,
  TruckOutlined,
  GiftOutlined,
  UserOutlined,
  LogoutOutlined,
  CrownOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

const menuItems = [
  { key: 'dashboard', icon: <DashboardOutlined />, label: '数据看板', plan: 'basic' },
  { type: 'divider' },
  { key: 'inventory', icon: <ShoppingCartOutlined />, label: '库存管理', plan: 'basic' },
  { key: 'risk-inspection', icon: <SafetyOutlined />, label: '风控体检', plan: 'basic' },
  { key: 'finance', icon: <DollarOutlined />, label: '财务结算', plan: 'basic' },
  { key: 'pricing-engine', icon: <ExperimentOutlined />, label: '核价引擎', plan: 'basic' },
  { key: 'analysis', icon: <BarChartOutlined />, label: '数据分析', plan: 'basic' },
  { type: 'divider' },
  { key: 'pricing', icon: <SettingOutlined />, label: '核价管理', plan: 'pro' },
  { key: 'api-sync', icon: <CloudSyncOutlined />, label: 'API同步', plan: 'pro' },
  { key: 'message', icon: <MessageOutlined />, label: '消息售后', plan: 'pro' },
  { key: 'scheduler', icon: <SettingOutlined />, label: '定时任务', plan: 'pro' },
  { key: 'shipping', icon: <TruckOutlined />, label: '物流发货', plan: 'pro' },
  { key: 'activity', icon: <GiftOutlined />, label: '活动管理', plan: 'pro' },
  { type: 'divider' },
  { key: 'factory-cost', icon: <ToolOutlined />, label: '工厂成本', plan: 'enterprise' },
  { key: 'supplier', icon: <TeamOutlined />, label: '供应商', plan: 'enterprise' },
  { key: 'product-research', icon: <SearchOutlined />, label: '选品分析', plan: 'enterprise' },
  { type: 'divider' },
  { key: 'admin', icon: <CrownOutlined />, label: '管理后台', plan: 'lifetime' },
];

const planLabels = { basic: '基础版', pro: '专业版', enterprise: '企业版', lifetime: '终身版' };

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();

  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const userPlan = user.plan || 'basic';

  const currentKey = location.pathname.split('/')[1] || 'dashboard';

  const handleMenuClick = ({ key }) => {
    navigate(`/${key}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const userMenu = {
    items: [
      { key: 'profile', icon: <UserOutlined />, label: `${user.email || user.nickname || '用户'}` },
      { type: 'divider' },
      { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
    ],
    onClick: ({ key }) => {
      if (key === 'logout') handleLogout();
    },
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
        width={220}
        style={{ borderRight: '1px solid #f0f0f0' }}
      >
        <div style={{
          height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontSize: collapsed ? 16 : 18, fontWeight: 'bold',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
        }}>
          {collapsed ? '🤖' : '🤖 卖家运营工具'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[currentKey]}
          items={menuItems.map((item) => {
            if (item.type === 'divider') return { type: 'divider' };
            const hasAccess = (
              (userPlan === 'lifetime') ||
              ({ basic: 0, pro: 1, enterprise: 2 }[userPlan] || 0) >=
              ({ basic: 0, pro: 1, enterprise: 2 }[item.plan] || 0)
            );
            return {
              key: item.key,
              icon: item.icon,
              label: (
                <span>
                  {item.label}
                  {!hasAccess && (
                    <span style={{ float: 'right', fontSize: 11, color: '#faad14' }}>🔒</span>
                  )}
                </span>
              ),
              disabled: !hasAccess,
            };
          })}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{
          padding: '0 24px', background: colorBgContainer,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          borderBottom: '1px solid #f0f0f0',
        }}>
          <Text type="secondary" style={{ fontSize: 14 }}>
            {currentKey.charAt(0).toUpperCase() + currentKey.slice(1)}
          </Text>
          <Dropdown menu={userMenu} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#667eea' }} />
              <Text>{user.email || user.nickname || '用户'}</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                ({planLabels[userPlan] || userPlan})
              </Text>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24 }}>
          <div style={{ padding: 24, minHeight: 360, background: colorBgContainer, borderRadius: borderRadiusLG }}>
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

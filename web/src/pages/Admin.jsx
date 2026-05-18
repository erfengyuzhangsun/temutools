import React, { useState, useEffect, useCallback } from 'react';
import { Table, Card, Input, Button, Tag, Modal, Select, Space, Typography, App, Badge, Tabs, Form, InputNumber, Popconfirm, Statistic, Row, Col } from 'antd';
import { SearchOutlined, CrownOutlined, ReloadOutlined, UserOutlined, ShoppingCartOutlined, MonitorOutlined, ToolOutlined, PlusOutlined } from '@ant-design/icons';
import {
  adminListUsers, adminUpgradePlan, adminRenewUser, adminToggleUser,
  adminDeleteUser, adminResetPassword,
  adminListOrders, adminCompleteOrder, adminDeleteOrder, adminMonitor
} from '../api/client';

const { Title } = Typography;

const planColors = { basic: 'default', pro: 'blue', enterprise: 'purple', lifetime: 'gold' };
const planLabels = { basic: '基础版', pro: '专业版', enterprise: '企业版', lifetime: '终身版' };

export default function AdminPage() {
  const { message } = App.useApp();
  const [tabKey, setTabKey] = useState('users');

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>
        <CrownOutlined style={{ marginRight: 8 }} />
        管理后台
      </Title>
      <Tabs activeKey={tabKey} onChange={setTabKey} items={[
        { key: 'users', label: <span><UserOutlined /> 用户管理</span>, children: <UserManagement /> },
        { key: 'orders', label: <span><ShoppingCartOutlined /> 订单管理</span>, children: <OrderManagement /> },
        { key: 'monitor', label: <span><MonitorOutlined /> 云主机监控</span>, children: <ServerMonitor /> },
        { key: 'maintain', label: <span><ToolOutlined /> 系统维护</span>, children: <SystemMaintenance /> },
      ]} />
    </div>
  );
}

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [upgradeModal, setUpgradeModal] = useState(null);
  const [upgradePlan, setUpgradePlan] = useState('pro');
  const [upgrading, setUpgrading] = useState(false);
  const [renewModal, setRenewModal] = useState(null);
  const [renewDays, setRenewDays] = useState(30);
  const [resetPwdModal, setResetPwdModal] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const { message } = App.useApp();

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await adminListUsers({ search, page, page_size: pageSize });
      setUsers(resp.data.users || []);
      setTotal(resp.data.total || 0);
    } catch {
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  }, [search, page, pageSize, message]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleUpgrade = async () => {
    if (!upgradeModal) return;
    setUpgrading(true);
    try {
      await adminUpgradePlan(upgradeModal.email, upgradePlan);
      message.success(`已将 ${upgradeModal.email} 升级为 ${planLabels[upgradePlan]}`);
      setUpgradeModal(null);
      fetchUsers();
    } catch (err) {
      message.error(err?.error?.message || '升级失败');
    } finally {
      setUpgrading(false);
    }
  };

  const handleRenew = async () => {
    if (!renewModal) return;
    try {
      await adminRenewUser(renewModal.email, renewDays);
      message.success(`已将 ${renewModal.email} 续费 ${renewDays} 天`);
      setRenewModal(null);
      fetchUsers();
    } catch (err) {
      message.error(err?.error?.message || '续费失败');
    }
  };

  const handleToggle = async (email, active) => {
    try {
      await adminToggleUser(email, active);
      message.success(`${active ? '启用' : '禁用'} ${email} 成功`);
      fetchUsers();
    } catch (err) {
      message.error(err?.error?.message || '操作失败');
    }
  };

  const handleDelete = async (record) => {
    try {
      await adminDeleteUser(record.user_id);
      message.success(`已删除用户 ${record.email}`);
      fetchUsers();
    } catch (err) {
      message.error(err?.error?.message || '删除失败');
    }
  };

  const handleResetPassword = async () => {
    if (!resetPwdModal) return;
    if (!newPassword || newPassword.length < 6) {
      message.error('密码至少6位');
      return;
    }
    try {
      await adminResetPassword(resetPwdModal.email, newPassword);
      message.success(`已将 ${resetPwdModal.email} 的密码重置成功`);
      setResetPwdModal(null);
      setNewPassword('');
      fetchUsers();
    } catch (err) {
      message.error(err?.error?.message || '密码重置失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'user_id', key: 'user_id', width: 60 },
    { title: '邮箱', dataIndex: 'email', key: 'email', ellipsis: true },
    { title: '昵称', dataIndex: 'nickname', key: 'nickname', render: (v) => v || '-' },
    {
      title: '套餐', dataIndex: 'plan', key: 'plan', width: 110,
      render: (plan) => (
        <Tag color={planColors[plan]} icon={plan === 'lifetime' ? <CrownOutlined /> : null}>
          {planLabels[plan] || plan}
        </Tag>
      ),
    },
    {
      title: '到期时间', dataIndex: 'expire_date', key: 'expire_date', width: 140,
      render: (v) => {
        if (!v) return <Tag>永久</Tag>;
        const date = new Date(v);
        const daysLeft = Math.ceil((date - new Date()) / (1000 * 60 * 60 * 24));
        if (daysLeft < 0) return <Badge status="error" text={`${date.toLocaleDateString()} (已过期)`} />;
        if (daysLeft <= 7) return <Badge status="warning" text={`${date.toLocaleDateString()} (${daysLeft}天)`} />;
        return date.toLocaleDateString();
      },
    },
    { title: '注册时间', dataIndex: 'created_at', key: 'created_at', width: 110, render: (v) => v ? new Date(v).toLocaleDateString() : '-' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 70, render: (v) => v ? <Tag color="green">正常</Tag> : <Tag color="red">禁用</Tag> },
    {
      title: '操作', key: 'action', width: 340,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<CrownOutlined />}
            onClick={() => { setUpgradeModal(record); setUpgradePlan(record.plan === 'lifetime' ? 'lifetime' : record.plan === 'enterprise' ? 'lifetime' : record.plan === 'pro' ? 'enterprise' : 'pro'); }}
            disabled={record.plan === 'lifetime'}>升级</Button>
          <Button type="link" size="small" onClick={() => { setRenewModal(record); setRenewDays(30); }}>续费</Button>
          <Popconfirm title={`确定${record.is_active ? '禁用' : '启用'}该用户？`} onConfirm={() => handleToggle(record.email, !record.is_active)}>
            <Button type="link" size="small" danger={record.is_active}>{record.is_active ? '禁用' : '启用'}</Button>
          </Popconfirm>
          <Button type="link" size="small" onClick={() => setResetPwdModal(record)}>重置密码</Button>
          <Popconfirm title={`确定删除用户 ${record.email}？此操作不可恢复，用户的所有店铺数据也将一同删除！`} onConfirm={() => handleDelete(record)}>
            <Button type="link" size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16 }}>
          <Input.Search placeholder="搜索用户邮箱" allowClear onSearch={(v) => { setSearch(v); setPage(1); }} style={{ width: 300 }} prefix={<SearchOutlined />} />
          <Button icon={<ReloadOutlined />} onClick={fetchUsers}>刷新</Button>
          <Tag>共 {total} 位用户</Tag>
        </Space>
        <Table dataSource={users} columns={columns} rowKey="user_id" loading={loading}
          pagination={{ current: page, pageSize, total, showSizeChanger: true, showTotal: (t) => `共 ${t} 位用户`, onChange: (p, ps) => { setPage(p); setPageSize(ps); }}}
          size="middle" />
      </Card>

      <Modal title="升级套餐" open={!!upgradeModal} onOk={handleUpgrade} onCancel={() => setUpgradeModal(null)} confirmLoading={upgrading} okText="确认升级" cancelText="取消">
        {upgradeModal && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <p>用户：<strong>{upgradeModal.email}</strong></p>
            <p>当前套餐：<Tag color={planColors[upgradeModal.plan]}>{planLabels[upgradeModal.plan]}</Tag></p>
            <Select value={upgradePlan} onChange={setUpgradePlan} style={{ width: '100%' }}
              options={[{ value: 'pro', label: '专业版 - Pro' }, { value: 'enterprise', label: '企业版 - Enterprise' }, { value: 'lifetime', label: '终身版 - Lifetime' }]} />
          </Space>
        )}
      </Modal>

      <Modal title="续费用户" open={!!renewModal} onOk={handleRenew} onCancel={() => setRenewModal(null)} okText="确认续费" cancelText="取消">
        {renewModal && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <p>用户：<strong>{renewModal.email}</strong></p>
            <p>当前到期：{renewModal.expire_date ? new Date(renewModal.expire_date).toLocaleDateString() : '永久'}</p>
            <Form.Item label="续费天数"><InputNumber min={1} max={3650} value={renewDays} onChange={setRenewDays} style={{ width: '100%' }} /></Form.Item>
          </Space>
        )}
      </Modal>

      <Modal title="重置用户密码" open={!!resetPwdModal} onOk={handleResetPassword} onCancel={() => { setResetPwdModal(null); setNewPassword(''); }} okText="确认重置" cancelText="取消">
        {resetPwdModal && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <p>用户：<strong>{resetPwdModal.email}</strong></p>
            <Form.Item label="新密码" required>
              <Input.Password value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="输入新密码（至少6位）" />
            </Form.Item>
          </Space>
        )}
      </Modal>
    </>
  );
}

function OrderManagement() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const { message } = App.useApp();

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await adminListOrders();
      setOrders(resp.data.orders || []);
    } catch {
      message.error('获取订单列表失败');
    } finally {
      setLoading(false);
    }
  }, [message]);

  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  const handleComplete = async (orderId) => {
    try {
      await adminCompleteOrder(orderId);
      message.success('订单已标记为已处理');
      fetchOrders();
    } catch (err) {
      message.error(err?.error?.message || '操作失败');
    }
  };

  const handleDelete = async (orderId) => {
    try {
      await adminDeleteOrder(orderId);
      message.success('订单已删除');
      fetchOrders();
    } catch (err) {
      message.error(err?.error?.message || '删除失败');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'order_id', key: 'order_id', width: 60 },
    { title: '姓名', dataIndex: 'contact_name', key: 'contact_name' },
    { title: '手机号', dataIndex: 'phone', key: 'phone' },
    { title: '微信', dataIndex: 'wechat', key: 'wechat', render: (v) => v || '-' },
    { title: '套餐', dataIndex: 'plan_name', key: 'plan_name' },
    { title: '金额', dataIndex: 'amount', key: 'amount', render: (v) => v ? `¥${v}` : '-' },
    { title: '备注', dataIndex: 'notes', key: 'notes', ellipsis: true, render: (v) => v || '-' },
    {
      title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: (v) => v === 'pending' ? <Tag color="orange">待处理</Tag> : <Tag color="green">已处理</Tag>,
    },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 150, render: (v) => v ? new Date(v).toLocaleString() : '-' },
    {
      title: '操作', key: 'action', width: 160,
      render: (_, record) => (
        <Space>
          {record.status === 'pending' && (
            <Button type="link" size="small" onClick={() => handleComplete(record.order_id)}>标记已处理</Button>
          )}
          <Popconfirm title="确定删除此订单？" onConfirm={() => handleDelete(record.order_id)}>
            <Button type="link" size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ReloadOutlined />} onClick={fetchOrders}>刷新</Button>
        <Tag>共 {orders.length} 条订单</Tag>
        {orders.filter(o => o.status === 'pending').length > 0 && (
          <Tag color="orange">{orders.filter(o => o.status === 'pending').length} 条待处理</Tag>
        )}
      </Space>
      <Table dataSource={orders} columns={columns} rowKey="order_id" loading={loading} size="middle" pagination={{ pageSize: 20 }} />
    </Card>
  );
}

function ServerMonitor() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const { message } = App.useApp();

  const check = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await adminMonitor();
      setReport(resp.data);
    } catch {
      message.error('健康检查失败');
    } finally {
      setLoading(false);
    }
  }, [message]);

  useEffect(() => { check(); }, [check]);

  const statusColor = (s) => s === 'normal' ? '#3f8600' : s === 'warning' ? '#faad14' : '#cf1322';
  const statusLabel = (s) => s === 'normal' ? '✅ 正常' : s === 'warning' ? '⚠️ 偏高' : '🔴 危险';

  return (
    <Card>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ReloadOutlined />} onClick={check} loading={loading}>立即检查</Button>
      </Space>
      {report && (
        <>
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Card><Statistic title="健康评分" value={report.health_score} suffix="/100" prefix="🏥" valueStyle={{ color: report.health_score > 70 ? '#3f8600' : '#cf1322' }} /></Card>
            </Col>
            <Col span={6}>
              <Card><Statistic title="运行时间" value={report.uptime} valueStyle={{ fontSize: 16 }} /></Card>
            </Col>
            <Col span={6}>
              <Card><Statistic title="整体状态" value={report.status === 'healthy' ? '健康' : report.status === 'degraded' ? '降级' : '警告'} valueStyle={{ color: statusColor(report.status) }} /></Card>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Card size="small" title="🖥️ CPU">
                <Statistic title="使用率" value={report.cpu?.usage_percent?.toFixed(1)} suffix="%" valueStyle={{ color: statusColor(report.cpu?.status) }} />
                <Tag color={report.cpu?.status === 'normal' ? 'green' : 'orange'} style={{ marginTop: 8 }}>{statusLabel(report.cpu?.status)}</Tag>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" title="💾 内存">
                <Statistic title="使用率" value={report.memory?.usage_percent?.toFixed(1)} suffix="%" valueStyle={{ color: statusColor(report.memory?.status) }} />
                <Tag color={report.memory?.status === 'normal' ? 'green' : 'orange'} style={{ marginTop: 8 }}>{statusLabel(report.memory?.status)}</Tag>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" title="💿 磁盘">
                <Statistic title="状态" value={report.disk?.status === 'normal' ? '正常' : '异常'} valueStyle={{ color: statusColor(report.disk?.status) }} />
                <Tag color={report.disk?.status === 'normal' ? 'green' : 'orange'} style={{ marginTop: 8 }}>{statusLabel(report.disk?.status)}</Tag>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </Card>
  );
}

function SystemMaintenance() {
  const { message } = App.useApp();
  const [exporting, setExporting] = useState(false);

  return (
    <Card>
      <Space direction="vertical" style={{ width: '100%' }}>
        <p style={{ fontSize: 16, fontWeight: 600 }}>🔄 系统维护</p>
        <Button>清除过期用户</Button>
        <Button>清理无用数据</Button>
      </Space>
    </Card>
  );
}

import React, { useState, useEffect, useCallback } from 'react';
import { Table, Card, Input, Button, Tag, Modal, Select, Space, Typography, App, Badge } from 'antd';
import { SearchOutlined, CrownOutlined, ReloadOutlined } from '@ant-design/icons';
import { adminListUsers, adminUpgradePlan } from '../api/client';

const { Title } = Typography;

const planColors = {
  basic: 'default',
  pro: 'blue',
  enterprise: 'purple',
  lifetime: 'gold',
};

const planLabels = {
  basic: '基础版',
  pro: '专业版',
  enterprise: '企业版',
  lifetime: '终身版',
};

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [upgradeModal, setUpgradeModal] = useState(null);
  const [upgradePlan, setUpgradePlan] = useState('pro');
  const [upgrading, setUpgrading] = useState(false);
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

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleSearch = (value) => {
    setSearch(value);
    setPage(1);
  };

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

  const columns = [
    {
      title: 'ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 60,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      ellipsis: true,
    },
    {
      title: '昵称',
      dataIndex: 'nickname',
      key: 'nickname',
      render: (v) => v || '-',
    },
    {
      title: '套餐',
      dataIndex: 'plan',
      key: 'plan',
      width: 120,
      render: (plan) => (
        <Tag color={planColors[plan]} icon={plan === 'lifetime' ? <CrownOutlined /> : null}>
          {planLabels[plan] || plan}
        </Tag>
      ),
    },
    {
      title: '到期时间',
      dataIndex: 'expire_date',
      key: 'expire_date',
      width: 130,
      render: (v) => {
        if (!v) return <Tag>永久</Tag>;
        const date = new Date(v);
        const daysLeft = Math.ceil((date - new Date()) / (1000 * 60 * 60 * 24));
        if (daysLeft < 0) return <Badge status="error" text={`${date.toLocaleDateString()} (已过期)`} />;
        if (daysLeft <= 7) return <Badge status="warning" text={`${date.toLocaleDateString()} (${daysLeft}天)`} />;
        return date.toLocaleDateString();
      },
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 130,
      render: (v) => v ? new Date(v).toLocaleDateString() : '-',
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (v) => v ? <Tag color="green">正常</Tag> : <Tag color="red">禁用</Tag>,
    },
    {
      title: '操作',
      key: 'action',
      width: 160,
      render: (_, record) => (
        <Button
          type="link"
          icon={<CrownOutlined />}
          onClick={() => {
            setUpgradeModal(record);
            setUpgradePlan(
              record.plan === 'basic' ? 'pro' :
              record.plan === 'pro' ? 'enterprise' :
              record.plan === 'enterprise' ? 'lifetime' : 'lifetime'
            );
          }}
          disabled={record.plan === 'lifetime'}
        >
          升级套餐
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>
        <CrownOutlined style={{ marginRight: 8 }} />
        用户管理
      </Title>

      <Card style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16 }}>
          <Input.Search
            placeholder="搜索用户邮箱"
            allowClear
            onSearch={handleSearch}
            style={{ width: 300 }}
            prefix={<SearchOutlined />}
          />
          <Button icon={<ReloadOutlined />} onClick={fetchUsers}>刷新</Button>
          <Tag style={{ marginLeft: 8 }}>共 {total} 位用户</Tag>
        </Space>

        <Table
          dataSource={users}
          columns={columns}
          rowKey="user_id"
          loading={loading}
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 位用户`,
            onChange: (p, ps) => { setPage(p); setPageSize(ps); },
          }}
          size="middle"
        />
      </Card>

      <Modal
        title="升级用户套餐"
        open={!!upgradeModal}
        onOk={handleUpgrade}
        onCancel={() => setUpgradeModal(null)}
        confirmLoading={upgrading}
        okText="确认升级"
        cancelText="取消"
      >
        {upgradeModal && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <p>用户邮箱：<strong>{upgradeModal.email}</strong></p>
            <p>当前套餐：<Tag color={planColors[upgradeModal.plan]}>{planLabels[upgradeModal.plan]}</Tag></p>
            <p>选择目标套餐：</p>
            <Select
              value={upgradePlan}
              onChange={setUpgradePlan}
              style={{ width: '100%' }}
              options={[
                { value: 'pro', label: '专业版 - Pro' },
                { value: 'enterprise', label: '企业版 - Enterprise' },
                { value: 'lifetime', label: '终身版 - Lifetime' },
              ]}
            />
          </Space>
        )}
      </Modal>
    </div>
  );
}

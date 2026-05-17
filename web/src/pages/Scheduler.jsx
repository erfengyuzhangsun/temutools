import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Tag, Spin, message, Typography, Row, Modal, Input, Switch } from 'antd';
import { ClockCircleOutlined, PlayCircleOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { getSchedulerTasks, createTask, deleteTask, runTaskNow } from '../api/client';

const { Title } = Typography;

export default function SchedulerPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createModal, setCreateModal] = useState(false);
  const [form, setForm] = useState({ taskId: '', name: '', cronExpression: '', description: '' });

  const fetchTasks = () => {
    setLoading(true);
    getSchedulerTasks().then((r) => setTasks(r.data?.tasks || [])).catch(() => setTasks([])).finally(() => setLoading(false));
  };

  useEffect(() => { fetchTasks(); }, []);

  const handleCreate = async () => {
    if (!form.taskId || !form.name || !form.cronExpression) { message.warning('请填写必填字段'); return; }
    await createTask(form.taskId, form.name, form.cronExpression, form.description);
    message.success('任务创建成功');
    setCreateModal(false);
    setForm({ taskId: '', name: '', cronExpression: '', description: '' });
    fetchTasks();
  };

  const handleRun = async (id) => {
    await runTaskNow(id);
    message.success('任务已触发');
  };

  const handleDelete = async (id) => {
    await deleteTask(id);
    message.success('任务已删除');
    fetchTasks();
  };

  const columns = [
    { title: '任务ID', dataIndex: 'task_id', key: 'task_id' },
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: 'Cron表达式', dataIndex: 'cron_expression', key: 'cron_expression' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (v) => <Tag color={v === 'running' ? 'blue' : 'default'}>{v || 'idle'}</Tag> },
    { title: '执行次数', dataIndex: 'run_count', key: 'run_count' },
    { title: '失败次数', dataIndex: 'fail_count', key: 'fail_count', render: (v) => v > 0 ? <Tag color="red">{v}</Tag> : v },
    { title: '启用', dataIndex: 'enabled', key: 'enabled', render: (v) => <Switch checked={v} disabled size="small" /> },
    {
      title: '操作', key: 'action', render: (_, r) => (
        <Space><Button size="small" icon={<PlayCircleOutlined />} onClick={() => handleRun(r.task_id)}>执行</Button><Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.task_id)}>删除</Button></Space>
      ),
    },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Title level={4}><ClockCircleOutlined /> 定时任务</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModal(true)}>新建任务</Button>
      </Row>
      <Card><Table dataSource={tasks} columns={columns} rowKey="task_id" pagination={false} size="small" /></Card>
      <Modal title="新建定时任务" open={createModal} onOk={handleCreate} onCancel={() => setCreateModal(false)}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input value={form.taskId} onChange={(e) => setForm({...form, taskId: e.target.value})} placeholder="任务ID *" />
          <Input value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} placeholder="任务名称 *" />
          <Input value={form.cronExpression} onChange={(e) => setForm({...form, cronExpression: e.target.value})} placeholder="Cron表达式 * (如: 0 */6 * * * *)" />
          <Input value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} placeholder="描述" />
        </Space>
      </Modal>
    </div>
  );
}

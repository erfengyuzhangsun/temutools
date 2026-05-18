import axios from 'axios';

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error.response?.data || error);
  }
);

export function login(email, password) {
  return client.post('/auth/login', { email, password });
}

export function register(email, password) {
  return client.post('/auth/register', { email, password });
}

export function getCurrentUser() {
  return client.get('/auth/me');
}

export function getDashboardOverview() {
  return client.get('/dashboard/overview');
}

export function getDashboardAlerts() {
  return client.get('/dashboard/alerts');
}

export function getInventoryList() {
  return client.get('/inventory/list');
}

export function syncInventory(shopId) {
  return client.post('/inventory/sync', { shop_id: shopId });
}

export function getAnalysisReport() {
  return client.get('/analysis/report');
}

export function getFinanceMonthly() {
  return client.get('/finance/monthly');
}

export function getFinanceForecast() {
  return client.get('/finance/forecast');
}

export function getPricingLogs(shopId, limit) {
  return client.get('/pricing/logs', { params: { shop_id: shopId, limit } });
}

export function autoHandlePricing(shopId) {
  return client.post('/pricing/auto-handle', { shop_id: shopId });
}

export function getApiSyncShops() {
  return client.get('/api-sync/shops');
}

export function bindShop(shopName, accessToken, region = 'us') {
  return client.post('/api-sync/bind-shop', { shop_name: shopName, access_token: accessToken, region });
}

export function syncOrders(shopId) {
  return client.post('/api-sync/sync-orders', { shop_id: shopId });
}

export function getSchedulerTasks() {
  return client.get('/scheduler/tasks');
}

export function createTask(taskId, name, cronExpression, description) {
  return client.post('/scheduler/tasks', { task_id: taskId, name, cron_expression: cronExpression, description });
}

export function deleteTask(taskId) {
  return client.delete(`/scheduler/tasks/${taskId}`);
}

export function runTaskNow(taskId) {
  return client.post(`/scheduler/tasks/${taskId}/run`);
}

export function getRiskReport() {
  return client.get('/risk-inspection/report');
}

export function getMessages() {
  return client.get('/message/list');
}

export function getActivities() {
  return client.get('/activity/list');
}

export function getFactoryProducts() {
  return client.get('/factory-cost/products');
}

export function createFactoryProduct(data) {
  return client.post('/factory-cost/product', data);
}

export function getFactoryAnalysis() {
  return client.get('/factory-cost/analysis');
}

export function getSuppliers() {
  return client.get('/supplier/list');
}

export function addSupplier(data) {
  return client.post('/supplier/add', data);
}

export function calculatePrice(costPrice, expectedMargin) {
  return client.post('/pricing-engine/calculate', { cost_price: costPrice, expected_margin: expectedMargin });
}

export function batchCalculate(items) {
  return client.post('/pricing-engine/batch', { items });
}

export function runRiskGuardCheck() {
  return client.post('/risk-guard/check');
}

export function getApiGuide() {
  return client.get('/api-guide/guide');
}

export function adminListUsers(params) {
  return client.get('/admin/users', { params });
}

export function adminUpgradePlan(email, planType) {
  return client.post('/admin/upgrade-plan', { email, plan_type: planType });
}

export function adminRenewUser(email, days) {
  return client.post('/admin/users/renew', { email, days });
}

export function adminToggleUser(email, active) {
  return client.post('/admin/users/toggle', { email, active });
}

export function adminListOrders() {
  return client.get('/admin/orders');
}

export function adminCompleteOrder(orderId) {
  return client.post('/admin/orders/complete', { order_id: orderId });
}

export function adminDeleteOrder(orderId) {
  return client.post('/admin/orders/delete', { order_id: orderId });
}

export function adminMonitor() {
  return client.get('/admin/monitor');
}

export function submitOrder(data) {
  return client.post('/submit-order', data);
}

export default client;

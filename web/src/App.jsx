import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import AppLayout from './components/AppLayout';
import LandingPage from './pages/Landing';
import LoginPage from './pages/Login';
import DashboardPage from './pages/Dashboard';
import InventoryPage from './pages/Inventory';
import AnalysisPage from './pages/Analysis';
import FinancePage from './pages/Finance';
import PricingPage from './pages/Pricing';
import ApiSyncPage from './pages/ApiSync';
import SchedulerPage from './pages/Scheduler';
import RiskInspectionPage from './pages/RiskInspection';
import FactoryCostPage from './pages/FactoryCost';
import SupplierPage from './pages/Supplier';
import PricingEnginePage from './pages/PricingEngine';
import MessagePage from './pages/Message';
import ActivityPage from './pages/Activity';
import RiskGuardPage from './pages/RiskGuard';
import ShippingPage from './pages/Shipping';
import AfterSalePage from './pages/AfterSale';
import ExchangePage from './pages/Exchange';
import ApiGuidePage from './pages/ApiGuide';
import AdminPage from './pages/Admin';
import PrivacyPage from './pages/Privacy';
import TermsPage from './pages/Terms';
import GuidePage from './pages/Guide';
import PlaceholderPage from './pages/PlaceholderPage';
import {
  ShoppingCartOutlined, BarChartOutlined, DollarOutlined,
  SettingOutlined, CloudSyncOutlined, ClockCircleOutlined,
  SafetyOutlined, ToolOutlined, TeamOutlined,
  ExperimentOutlined, MessageOutlined, GiftOutlined,
  SearchOutlined, AppstoreOutlined, FileTextOutlined,
  TruckOutlined,
} from '@ant-design/icons';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

const placeholderModules = [
  { path: 'review-monitor', label: '差评监控', icon: <FileTextOutlined /> },
  { path: 'batch-ops', label: '批量操作', icon: <AppstoreOutlined /> },
  { path: 'product-research', label: '选品分析', icon: <SearchOutlined /> },
];

export default function App() {
  return (
    <ConfigProvider locale={zhCN} theme={{
      token: { colorPrimary: '#667eea', borderRadius: 8 },
    }}>
      <AntApp>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="/terms" element={<TermsPage />} />
            <Route path="/guide" element={<GuidePage />} />
            <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/finance" element={<FinancePage />} />
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/api-sync" element={<ApiSyncPage />} />
              <Route path="/scheduler" element={<SchedulerPage />} />
              <Route path="/risk-inspection" element={<RiskInspectionPage />} />
              <Route path="/factory-cost" element={<FactoryCostPage />} />
              <Route path="/supplier" element={<SupplierPage />} />
              <Route path="/pricing-engine" element={<PricingEnginePage />} />
              <Route path="/message" element={<MessagePage />} />
              <Route path="/activity" element={<ActivityPage />} />
              <Route path="/risk-guard" element={<RiskGuardPage />} />
              <Route path="/shipping" element={<ShippingPage />} />
              <Route path="/aftersale" element={<AfterSalePage />} />
              <Route path="/exchange" element={<ExchangePage />} />
              <Route path="/api-guide" element={<ApiGuidePage />} />
              <Route path="/admin" element={<AdminPage />} />
              {placeholderModules.map((m) => (
                <Route key={m.path} path={`/${m.path}`} element={<PlaceholderPage title={m.label} icon={m.icon} />} />
              ))}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  );
}

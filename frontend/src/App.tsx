import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import AuditReportsPage from './pages/AuditReportsPage';
import DashboardPage from './pages/DashboardPage';
import DecisionDetailPage from './pages/DecisionDetailPage';
import DecisionsPage from './pages/DecisionsPage';
import EvidencePage from './pages/EvidencePage';
import EvidenceDetailPage from './pages/EvidenceDetailPage';
import NotFoundPage from './pages/NotFoundPage';
import PoliciesPage from './pages/PoliciesPage';
import PolicyDetailPage from './pages/PolicyDetailPage';
import ReplayPage from './pages/ReplayPage';
import ReplayDetailPage from './pages/ReplayDetailPage';

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/decisions" element={<DecisionsPage />} />
        <Route path="/decisions/:decisionId" element={<DecisionDetailPage />} />
        <Route path="/evidence" element={<EvidencePage />} />
        <Route path="/evidence/:evidenceId" element={<EvidenceDetailPage />} />
        <Route path="/policies" element={<PoliciesPage />} />
        <Route path="/policies/:policyId" element={<PolicyDetailPage />} />
        <Route path="/replay" element={<ReplayPage />} />
        <Route path="/replay/:replayId" element={<ReplayDetailPage />} />
        <Route path="/audit-reports" element={<AuditReportsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

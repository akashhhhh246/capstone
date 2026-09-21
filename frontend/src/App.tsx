import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { darkTheme } from './theme/theme';
import { MainLayout } from './layouts/MainLayout';
import { DashboardPage } from './pages/DashboardPage';
import { LiveDataPage } from './pages/LiveDataPage';
import { ContentAnalysisPage } from './pages/ContentAnalysisPage';
import { ProvenanceExplorerPage } from './pages/ProvenanceExplorerPage';
import { PropagationAnalysisPage } from './pages/PropagationAnalysisPage';
import { CampaignAnalysisPage } from './pages/CampaignAnalysisPage';
import { SimulationPage } from './pages/SimulationPage';
import { ModelGovernancePage } from './pages/ModelGovernancePage';
import { ErrorBoundary } from './components/ErrorBoundary';

export const App: React.FC = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <ErrorBoundary fallbackTitle="Defense Operations Platform Error">
        <Router>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="live-data" element={<LiveDataPage />} />
              <Route path="analysis" element={<ContentAnalysisPage />} />
              <Route path="provenance" element={<ProvenanceExplorerPage />} />
              <Route path="propagation" element={<PropagationAnalysisPage />} />
              <Route path="campaigns" element={<CampaignAnalysisPage />} />
              <Route path="simulation" element={<SimulationPage />} />
              <Route path="models" element={<ModelGovernancePage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </Router>
      </ErrorBoundary>
    </ThemeProvider>
  );
};

export default App;

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConsoleLayout } from './layouts/ConsoleLayout';

// Pages
import { OverviewPage } from './pages/Overview';
import { MissionCenterPage } from './pages/MissionCenter';
import { LiveOperationPage } from './pages/LiveOperation';
import { RootCausePage } from './pages/RootCause';
import { OutcomeGuardianPage } from './pages/OutcomeGuardian';
import { WhatIfLabPage } from './pages/WhatIfLab';
import { OperatorPassportPage } from './pages/OperatorPassport';
import { TrainingForgePage } from './pages/TrainingForge';
import { OperationalMemoryPage } from './pages/OperationalMemory';
import { SiteStabilityPage } from './pages/SiteStability';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10000,
      refetchOnWindowFocus: false,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ConsoleLayout>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            
            <Route path="/missions" element={<MissionCenterPage />} />
            <Route path="/missions/:missionId" element={<MissionCenterPage />} />

            <Route path="/live" element={<LiveOperationPage />} />
            <Route path="/live/:missionId" element={<LiveOperationPage />} />

            <Route path="/root-cause" element={<RootCausePage />} />
            <Route path="/root-cause/:missionId" element={<RootCausePage />} />

            <Route path="/outcome-guardian" element={<OutcomeGuardianPage />} />
            <Route path="/outcome-guardian/:missionId" element={<OutcomeGuardianPage />} />

            <Route path="/what-if" element={<WhatIfLabPage />} />
            <Route path="/what-if/:missionId" element={<WhatIfLabPage />} />

            <Route path="/operators" element={<OperatorPassportPage />} />
            <Route path="/operators/:operatorId" element={<OperatorPassportPage />} />

            {/* Stretch Roadmap Vision Mocks */}
            <Route path="/training-forge" element={<TrainingForgePage />} />
            <Route path="/operational-memory" element={<OperationalMemoryPage />} />
            <Route path="/site-stability" element={<SiteStabilityPage />} />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ConsoleLayout>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;

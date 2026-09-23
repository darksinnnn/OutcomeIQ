import React from 'react';
import { ConsoleRail } from '../components/common/ConsoleRail';
import { EvidenceDrawer } from '../components/evidence/EvidenceDrawer';

interface ConsoleLayoutProps {
  children: React.ReactNode;
}

export const ConsoleLayout: React.FC<ConsoleLayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-base text-text-primary">
      {/* Console Nav Rail */}
      <ConsoleRail />

      {/* Main Workspace Viewport */}
      <main className="flex-1 flex flex-col min-w-0 min-h-screen relative">
        <div className="flex-1 p-4 md:p-6 max-w-[1600px] w-full mx-auto">
          {children}
        </div>
      </main>

      {/* Slide-over Evidence Drawer */}
      <EvidenceDrawer />
    </div>
  );
};

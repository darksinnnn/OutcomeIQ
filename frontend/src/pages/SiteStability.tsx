import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { Compass, ShieldAlert, Activity } from 'lucide-react';

export const SiteStabilityPage: React.FC = () => {
  return (
    <div>
      <PageHeader
        title="Site Stability Engine — Multi-Signal Synthesis"
        subtitle="Combines weak signals across multiple active missions into a holistic site stability score."
        badgeText="Roadmap Vision Mock"
      />

      <div className="bg-panel border border-hairline rounded-md p-8 text-center space-y-4 max-w-2xl mx-auto my-12">
        <div className="w-16 h-16 rounded-full bg-status-green/15 text-status-green flex items-center justify-center mx-auto border border-status-green/30">
          <Compass className="w-8 h-8" />
        </div>
        <div>
          <span className="text-[10px] font-display uppercase tracking-widest px-2.5 py-1 rounded-sm bg-hairline text-text-muted border border-hairline font-semibold">
            Roadmap Concept — Site Intelligence
          </span>
          <h2 className="font-display text-xl font-bold text-text-primary mt-3">
            Holistic Jobsite Stability Engine
          </h2>
          <p className="text-xs font-body text-text-secondary mt-2 leading-relaxed">
            Evaluates cross-zone systemic risk when multiple minor deviations (weather + truck lag + grade error) compound into site-wide schedule risk.
          </p>
        </div>

        <div className="pt-4 border-t border-hairline grid grid-cols-3 gap-3 text-center font-display text-xs">
          <div className="bg-base p-3 rounded-sm border border-hairline">
            <span className="text-text-muted block text-[10px] uppercase">North Zone</span>
            <span className="font-bold text-status-amber text-sm">Watch</span>
          </div>
          <div className="bg-base p-3 rounded-sm border border-hairline">
            <span className="text-text-muted block text-[10px] uppercase">East Trench</span>
            <span className="font-bold text-status-green text-sm">Stable</span>
          </div>
          <div className="bg-base p-3 rounded-sm border border-hairline">
            <span className="text-text-muted block text-[10px] uppercase">South Grade</span>
            <span className="font-bold text-status-red text-sm">Elevated</span>
          </div>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { BrainCircuit, Database, Layers } from 'lucide-react';

export const OperationalMemoryPage: React.FC = () => {
  return (
    <div>
      <PageHeader
        title="Operational Memory — Cross-Mission Knowledge Base"
        subtitle="Persists site-level learned causal patterns across missions and operators for continuous jobsite learning."
        badgeText="Roadmap Vision Mock"
      />

      <div className="bg-panel border border-hairline rounded-md p-8 text-center space-y-4 max-w-2xl mx-auto my-12">
        <div className="w-16 h-16 rounded-full bg-data-blue/15 text-data-blue flex items-center justify-center mx-auto border border-data-blue/30">
          <BrainCircuit className="w-8 h-8" />
        </div>
        <div>
          <span className="text-[10px] font-display uppercase tracking-widest px-2.5 py-1 rounded-sm bg-hairline text-text-muted border border-hairline font-semibold">
            Roadmap Concept — Long-Term Memory
          </span>
          <h2 className="font-display text-xl font-bold text-text-primary mt-3">
            Site-Wide Operational Memory Store
          </h2>
          <p className="text-xs font-body text-text-secondary mt-2 leading-relaxed">
            Operational Memory captures validated causal chains (e.g. "Rain + 30% soil moisture requires 1 extra haul truck to prevent excavator queue idle") and indexes them for future project planning.
          </p>
        </div>

        <div className="pt-4 border-t border-hairline space-y-2 text-left text-xs font-body">
          <div className="bg-base p-3 rounded-sm border border-hairline flex items-center justify-between">
            <span className="font-display font-medium text-text-primary">Pattern #891: Haul Loop Queuing in Rain</span>
            <span className="text-accent font-mono">Verified 18x</span>
          </div>
          <div className="bg-base p-3 rounded-sm border border-hairline flex items-center justify-between">
            <span className="font-display font-medium text-text-primary">Pattern #904: Subgrade Elev Error vs Pass Count</span>
            <span className="text-status-green font-mono">Verified 42x</span>
          </div>
        </div>
      </div>
    </div>
  );
};

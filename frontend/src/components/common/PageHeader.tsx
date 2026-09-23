import React from 'react';
import { useUIStore } from '../../stores/uiStore';
import { SEEDED_MISSIONS } from '../../services/api';
import { Target, Layers, ChevronDown } from 'lucide-react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  badgeText?: string;
  children?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  badgeText = 'Mission Intelligence Loop',
  children,
}) => {
  const selectedMissionId = useUIStore((state) => state.selectedMissionId);
  const setSelectedMissionId = useUIStore((state) => state.setSelectedMissionId);
  const activeScenario = useUIStore((state) => state.activeScenarioFilter);
  const setActiveScenario = useUIStore((state) => state.setActiveScenarioFilter);

  const selectedMission = SEEDED_MISSIONS.find((m) => m.id === selectedMissionId) || SEEDED_MISSIONS[0];

  return (
    <div className="bg-panel border-b border-hairline px-6 py-4 mb-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-sm bg-accent/10 text-accent border border-accent/30 text-[11px] font-display font-medium">
              <Target className="w-3 h-3" />
              {badgeText}
            </span>
            {selectedMission.scenario_tag && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-sm bg-data-blue/10 text-data-blue border border-data-blue/30 text-[11px] font-display">
                <Layers className="w-3 h-3" />
                Scenario: {selectedMission.scenario_tag}
              </span>
            )}
          </div>
          <h1 className="font-display text-2xl font-semibold text-text-primary tracking-tight">
            {title}
          </h1>
          {subtitle && (
            <p className="text-text-secondary text-sm font-body mt-0.5">
              {subtitle}
            </p>
          )}
        </div>

        {/* Global Mission & Scenario Selectors */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <label className="text-[11px] font-body text-text-muted uppercase tracking-wider block mb-1">
              Active Mission
            </label>
            <div className="relative">
              <select
                value={selectedMissionId}
                onChange={(e) => setSelectedMissionId(e.target.value)}
                className="appearance-none bg-elevated text-text-primary text-xs font-display border border-hairline rounded-sm pl-3 pr-8 py-1.5 focus:outline-none focus:ring-2 focus:ring-accent cursor-pointer"
              >
                {SEEDED_MISSIONS.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.id} — {m.task_type} ({m.scenario_tag || 'Standard'})
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-text-muted absolute right-2.5 top-2.5 pointer-events-none" />
            </div>
          </div>

          {children}
        </div>
      </div>
    </div>
  );
};

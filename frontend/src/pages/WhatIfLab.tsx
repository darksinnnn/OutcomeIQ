import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { outcomeIQApi } from '../services/api';
import { useUIStore } from '../stores/uiStore';
import { PageHeader } from '../components/common/PageHeader';
import { StateWrapper } from '../components/common/StateWrapper';
import { BeforeAfterComparison } from '../components/modules/BeforeAfterComparison';
import { FlaskConical, Truck, UserCheck, Sun, ArrowRight, Play } from 'lucide-react';

export const WhatIfLabPage: React.FC = () => {
  const { missionId } = useParams<{ missionId?: string }>();
  const globalSelectedId = useUIStore((state) => state.selectedMissionId);

  const activeId = missionId || globalSelectedId;

  const [selectedIntervention, setSelectedIntervention] = useState<'add_truck' | 'swap_operator' | 'route_change'>('add_truck');

  const { data: simulationEnvelope, isLoading, isError, refetch } = useQuery({
    queryKey: ['what-if-simulation', activeId, selectedIntervention],
    queryFn: () =>
      outcomeIQApi.simulateWhatIf(activeId, {
        add_truck: selectedIntervention === 'add_truck',
        operator_id: selectedIntervention === 'swap_operator' ? 'OP-101' : undefined,
        route_change: selectedIntervention === 'route_change',
      }),
  });

  return (
    <div>
      <PageHeader
        title={`What-If Decision Lab — ${activeId}`}
        subtitle="Simulate the effect of operational decisions (add a truck, swap operator, optimize route) before dispatching interventions."
      />

      <div className="space-y-6">
        {/* Intervention Selection Buttons */}
        <div className="bg-panel border border-hairline rounded-md p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-hairline pb-3">
            <FlaskConical className="w-5 h-5 text-accent" />
            <h3 className="font-display font-semibold text-sm text-text-primary">
              Select Operational Intervention Hypothesis
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => setSelectedIntervention('add_truck')}
              className={`p-4 rounded-md border text-left flex items-start gap-3 transition-all ${
                selectedIntervention === 'add_truck'
                  ? 'bg-accent/15 border-accent text-text-primary ring-1 ring-accent'
                  : 'bg-base border-hairline text-text-secondary hover:text-text-primary hover:border-hairline'
              }`}
            >
              <div className="p-2 rounded-sm bg-accent/20 text-accent shrink-0 mt-0.5">
                <Truck className="w-5 h-5" />
              </div>
              <div>
                <span className="font-display font-semibold text-xs text-text-primary block">
                  Hypothesis 1: Dispatch +1 Haul Truck
                </span>
                <span className="text-[11px] font-body text-text-muted mt-1 block">
                  Eliminate loader waiting queue bottleneck in Zone North.
                </span>
              </div>
            </button>

            <button
              onClick={() => setSelectedIntervention('swap_operator')}
              className={`p-4 rounded-md border text-left flex items-start gap-3 transition-all ${
                selectedIntervention === 'swap_operator'
                  ? 'bg-accent/15 border-accent text-text-primary ring-1 ring-accent'
                  : 'bg-base border-hairline text-text-secondary hover:text-text-primary hover:border-hairline'
              }`}
            >
              <div className="p-2 rounded-sm bg-data-blue/20 text-data-blue shrink-0 mt-0.5">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <span className="font-display font-semibold text-xs text-text-primary block">
                  Hypothesis 2: Swap Operator to OP-101
                </span>
                <span className="text-[11px] font-body text-text-muted mt-1 block">
                  Assign operator with high wet-trenching capability evidence.
                </span>
              </div>
            </button>

            <button
              onClick={() => setSelectedIntervention('route_change')}
              className={`p-4 rounded-md border text-left flex items-start gap-3 transition-all ${
                selectedIntervention === 'route_change'
                  ? 'bg-accent/15 border-accent text-text-primary ring-1 ring-accent'
                  : 'bg-base border-hairline text-text-secondary hover:text-text-primary hover:border-hairline'
              }`}
            >
              <div className="p-2 rounded-sm bg-status-green/20 text-status-green shrink-0 mt-0.5">
                <Sun className="w-5 h-5" />
              </div>
              <div>
                <span className="font-display font-semibold text-xs text-text-primary block">
                  Hypothesis 3: Bypass Mud Patch
                </span>
                <span className="text-[11px] font-body text-text-muted mt-1 block">
                  Reroute haulers around soft clay section (+0.4km length).
                </span>
              </div>
            </button>
          </div>
        </div>

        {/* Simulation Result Output */}
        <StateWrapper isLoading={isLoading} isError={isError} onRetry={refetch}>
          {simulationEnvelope?.value && (
            <BeforeAfterComparison
              whatIfData={simulationEnvelope.value}
              confidence={simulationEnvelope.confidence}
              evidence={simulationEnvelope.evidence}
            />
          )}
        </StateWrapper>
      </div>
    </div>
  );
};

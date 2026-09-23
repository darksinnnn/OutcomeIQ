import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { outcomeIQApi } from '../services/api';
import { useUIStore } from '../stores/uiStore';
import { PageHeader } from '../components/common/PageHeader';
import { StateWrapper } from '../components/common/StateWrapper';
import { ConfidencePill } from '../components/common/ConfidencePill';
import { MetricDisplay } from '../components/common/MetricDisplay';
import { FileCheck2, ShieldCheck, ArrowRight, User, Truck, Clock, AlertCircle } from 'lucide-react';

export const MissionCenterPage: React.FC = () => {
  const navigate = useNavigate();
  const { missionId } = useParams<{ missionId?: string }>();
  const globalSelectedId = useUIStore((state) => state.selectedMissionId);

  const activeId = missionId || globalSelectedId;

  const { data: contractEnvelope, isLoading, isError, refetch } = useQuery({
    queryKey: ['mission-contract', activeId],
    queryFn: () => outcomeIQApi.getMissionContract(activeId),
  });

  const contract = contractEnvelope?.value;

  return (
    <div>
      <PageHeader
        title={`Mission Contract Center — ${activeId}`}
        subtitle="Turns raw work orders into structured targets: objective quantity, deadline, quality tolerance, & safety constraints."
      />

      <StateWrapper isLoading={isLoading} isError={isError} onRetry={refetch}>
        {contract && (
          <div className="space-y-6">
            {/* Header Contract Status Banner */}
            <div className="bg-panel border border-hairline rounded-md p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 rounded-sm bg-status-green/15 text-status-green border border-status-green/30 text-xs font-display font-medium">
                    Contract Validated & Active
                  </span>
                  <span className="text-xs font-mono text-text-muted">
                    Mission ID: {contract.mission_id}
                  </span>
                </div>
                <h2 className="font-display text-xl font-bold text-text-primary">
                  {contract.task_type}
                </h2>
              </div>

              <div className="flex items-center gap-3">
                <ConfidencePill
                  confidence={contractEnvelope.confidence}
                  evidence={contractEnvelope.evidence}
                  title="Mission Contract Validation"
                />

                <button
                  onClick={() => navigate(`/live/${contract.mission_id}`)}
                  className="px-4 py-2 bg-accent text-base font-display font-semibold text-xs rounded-sm hover:bg-accent/90 transition-colors flex items-center gap-2 shadow-sm"
                >
                  <span>Launch Live Operation</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Target & Tolerance Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricDisplay
                label="Objective Quantity"
                value={contract.objective_quantity}
                unit={contract.objective_unit}
                subtext="Verified Target Volume"
                color="amber"
                highlight
              />
              <MetricDisplay
                label="Quality Tolerance"
                value={`±${contract.quality_tolerance_cm}`}
                unit="cm"
                subtext="Elevation Grade Allowance"
                color="blue"
              />
              <MetricDisplay
                label="Safety Speed Limit"
                value={contract.safety_constraints?.max_speed_kph || 25}
                unit="km/h"
                subtext="Jobsite Speed Constraint"
                color="green"
              />
              <MetricDisplay
                label="Contract Deadline"
                value={new Date(contract.deadline).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                unit="24h"
                subtext={new Date(contract.deadline).toLocaleDateString()}
              />
            </div>

            {/* Resource & Safety Assignments */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-panel border border-hairline rounded-md p-5 space-y-4">
                <h3 className="font-display font-semibold text-sm text-text-primary uppercase tracking-wider flex items-center gap-2">
                  <User className="w-4 h-4 text-accent" />
                  Assigned Personnel & Equipment
                </h3>

                <div className="space-y-3 text-xs font-body">
                  <div className="flex items-center justify-between p-2.5 bg-base rounded-sm border border-hairline">
                    <span className="text-text-muted">Assigned Operator:</span>
                    <span className="font-display font-semibold text-text-primary">{contract.assigned_operator_id}</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 bg-base rounded-sm border border-hairline">
                    <span className="text-text-muted">Assigned Fleet Machine:</span>
                    <span className="font-display font-semibold text-text-primary">{contract.assigned_machine_id}</span>
                  </div>
                </div>
              </div>

              <div className="bg-panel border border-hairline rounded-md p-5 space-y-4">
                <h3 className="font-display font-semibold text-sm text-text-primary uppercase tracking-wider flex items-center gap-2">
                  <Truck className="w-4 h-4 text-accent" />
                  Assigned Jobsite Resources
                </h3>

                <div className="space-y-2 text-xs font-body">
                  {contract.assigned_resources?.map((res, idx) => (
                    <div key={idx} className="flex items-center gap-2 p-2 bg-base rounded-sm border border-hairline text-text-secondary">
                      <div className="w-2 h-2 rounded-full bg-accent" />
                      <span>{res}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </StateWrapper>
    </div>
  );
};

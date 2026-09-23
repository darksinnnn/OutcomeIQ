import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Mission } from '../../types';
import { useUIStore } from '../../stores/uiStore';
import { StatusChip } from '../common/StatusChip';
import { Clock, ArrowRight, User, Truck, ShieldCheck, AlertCircle } from 'lucide-react';

interface MissionCardProps {
  mission: Mission;
}

export const MissionCard: React.FC<MissionCardProps> = ({ mission }) => {
  const navigate = useNavigate();
  const setSelectedMissionId = useUIStore((state) => state.setSelectedMissionId);
  const openDrawer = useUIStore((state) => state.openEvidenceDrawer);

  const isQualityAlert = mission.status === 'quality_alert';
  const isFalseIdle = mission.scenario_tag === 'FALSE_IDLE';

  const handleSelect = () => {
    setSelectedMissionId(mission.id);
    navigate(`/live/${mission.id}`);
  };

  const handleExplain = (e: React.MouseEvent) => {
    e.stopPropagation();
    openDrawer({
      title: `Mission ${mission.id} Overview Evidence`,
      confidence: 0.92,
      evidence: [
        {
          factor: 'Telemetry Stream Integrity',
          weight_or_probability: 0.95,
          detail: `Telemetry stream active for ${mission.task_type}. 100% seatbelt compliance recorded.`,
        },
        {
          factor: 'Scenario Baseline',
          weight_or_probability: 0.89,
          detail: mission.scenario_tag
            ? `Seeded scenario active: ${mission.scenario_tag}.`
            : 'Standard mission execution baseline.',
        },
      ],
    });
  };

  return (
    <div
      onClick={handleSelect}
      className={`bg-panel border rounded-md p-5 transition-all duration-150 cursor-pointer hover:border-accent/40 group relative flex flex-col justify-between ${
        isQualityAlert ? 'border-status-red/40 bg-elevated/40' : 'border-hairline'
      }`}
    >
      {/* Top Meta Bar */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="font-display font-bold text-sm text-text-primary group-hover:text-accent transition-colors">
              {mission.id}
            </span>
            <span className="text-[11px] font-mono text-text-muted px-1.5 py-0.5 rounded-sm bg-base border border-hairline">
              {mission.zone_id}
            </span>
          </div>
          <StatusChip
            state={isQualityAlert ? 'red' : isFalseIdle ? 'amber' : 'green'}
            label={isQualityAlert ? 'Quality Watch' : isFalseIdle ? 'Time Drift' : 'On Track'}
            size="sm"
          />
        </div>

        {/* Mission Task Title */}
        <h3 className="font-display text-base font-medium text-text-primary mb-3">
          {mission.task_type}
        </h3>

        {/* Quantities & Parameters */}
        <div className="grid grid-cols-2 gap-3 mb-4 bg-base/50 p-2.5 rounded-sm border border-hairline/60">
          <div>
            <span className="text-[10px] font-display uppercase tracking-wider text-text-muted block">
              Objective Target
            </span>
            <span className="font-display text-xs font-semibold text-text-primary tabular-nums">
              {mission.objective_quantity} {mission.objective_unit}
            </span>
          </div>
          <div>
            <span className="text-[10px] font-display uppercase tracking-wider text-text-muted block">
              Naive Baseline ETA
            </span>
            <span className="font-display text-xs font-semibold text-text-secondary tabular-nums">
              {mission.naive_estimated_time_min} mins
            </span>
          </div>
        </div>

        {/* Resources & Operator Info */}
        <div className="space-y-1.5 text-xs text-text-secondary font-body mb-4">
          <div className="flex items-center gap-2">
            <User className="w-3.5 h-3.5 text-text-muted" />
            <span>Operator: <strong className="text-text-primary font-medium">{mission.assigned_operator_id}</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <Truck className="w-3.5 h-3.5 text-text-muted" />
            <span>Machine: <strong className="text-text-primary font-medium">{mission.assigned_machine_id}</strong></span>
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="pt-3 border-t border-hairline flex items-center justify-between mt-auto">
        <button
          onClick={handleExplain}
          className="text-[11px] font-display text-text-muted hover:text-accent flex items-center gap-1 transition-colors"
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Inspect Evidence</span>
        </button>

        <span className="text-xs font-display font-medium text-accent flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
          Open Live Console
          <ArrowRight className="w-3.5 h-3.5" />
        </span>
      </div>
    </div>
  );
};

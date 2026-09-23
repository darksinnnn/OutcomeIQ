import React from 'react';
import { OperatorCapabilityRecord } from '../../types';
import { useUIStore } from '../../stores/uiStore';
import { ConfidencePill } from '../common/ConfidencePill';
import { ShieldCheck, MessageSquare, Layers, CheckCircle2 } from 'lucide-react';

interface PassportCapabilityBarProps {
  record: OperatorCapabilityRecord;
}

export const PassportCapabilityBar: React.FC<PassportCapabilityBarProps> = ({ record }) => {
  const setContestingItem = useUIStore((state) => state.setContestingItem);
  const openDrawer = useUIStore((state) => state.openEvidenceDrawer);

  const confidencePct = Math.round(record.confidence * 100);

  const handleInspect = () => {
    openDrawer({
      title: `Operator Capability Evidence: ${record.task_type}`,
      confidence: record.confidence,
      evidence: [
        {
          factor: 'Sample Size & Verification Count',
          weight_or_probability: record.confidence,
          detail: `Based on ${record.sample_count} comparable missions (${record.success_count} successful outcomes) in ${record.material_type}.`,
        },
        {
          factor: 'Historical Duration Delta',
          weight_or_probability: 0.88,
          detail: `Average task completion duration delta ${record.avg_time_delta_pct > 0 ? '+' : ''}${record.avg_time_delta_pct}% versus baseline.`,
        },
        {
          factor: 'Quality Success Rate',
          weight_or_probability: 0.94,
          detail: `Quality tolerance compliance rate: ${record.avg_quality_success_pct}%.`,
        },
      ],
    });
  };

  return (
    <div className="bg-panel border border-hairline rounded-md p-4 space-y-3 hover:border-accent/30 transition-colors">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-hairline/60 pb-2.5">
        <div>
          <div className="flex items-center gap-2">
            <h4 className="font-display font-semibold text-sm text-text-primary">
              {record.task_type}
            </h4>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-base border border-hairline text-text-muted">
              {record.material_type}
            </span>
          </div>
          <p className="text-[11px] font-body text-text-muted mt-0.5">
            Context: {record.weather_condition} — Last verified {new Date(record.last_verified_at).toLocaleDateString()}
          </p>
        </div>

        <ConfidencePill confidence={record.confidence} title={`Capability: ${record.task_type}`} />
      </div>

      {/* Verified Sample Count & Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs font-display">
          <span className="text-text-secondary">
            Demonstrated Capability Level ({record.success_count} / {record.sample_count} missions successful)
          </span>
          <span className="text-accent font-semibold tabular-nums">
            {confidencePct}% Confidence
          </span>
        </div>
        <div className="w-full bg-hairline h-2 rounded-full overflow-hidden">
          <div
            className="bg-accent h-full transition-all duration-300"
            style={{ width: `${confidencePct}%` }}
          />
        </div>
      </div>

      {/* Quantitative Context Evidence Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-1 text-xs font-mono">
        <div className="bg-base/60 p-2 rounded-sm border border-hairline/40">
          <span className="text-[10px] font-display text-text-muted uppercase block">Sample Missions</span>
          <span className="font-bold text-text-primary tabular-nums">{record.sample_count}</span>
        </div>
        <div className="bg-base/60 p-2 rounded-sm border border-hairline/40">
          <span className="text-[10px] font-display text-text-muted uppercase block">Quality Success</span>
          <span className="font-bold text-status-green tabular-nums">{record.avg_quality_success_pct}%</span>
        </div>
        <div className="bg-base/60 p-2 rounded-sm border border-hairline/40 col-span-2 sm:col-span-1">
          <span className="text-[10px] font-display text-text-muted uppercase block">Avg Time Delta</span>
          <span className={`font-bold tabular-nums ${record.avg_time_delta_pct <= 0 ? 'text-status-green' : 'text-status-amber'}`}>
            {record.avg_time_delta_pct > 0 ? '+' : ''}{record.avg_time_delta_pct}%
          </span>
        </div>
      </div>

      {/* Contestability & Evidence Triggers */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={handleInspect}
          className="text-xs text-text-secondary hover:text-accent font-display flex items-center gap-1.5 transition-colors"
        >
          <ShieldCheck className="w-3.5 h-3.5 text-accent" />
          <span>View Traceable Evidence</span>
        </button>

        <button
          onClick={() => setContestingItem({ id: record.id, context: `${record.task_type} (${record.material_type})` })}
          className="text-[11px] text-text-muted hover:text-text-primary font-display flex items-center gap-1 transition-colors"
          title="Contest or add operator annotation to this evidence record"
        >
          <MessageSquare className="w-3 h-3" />
          <span>Annotate / Contest</span>
        </button>
      </div>
    </div>
  );
};

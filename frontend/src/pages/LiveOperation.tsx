import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { outcomeIQApi } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import { useUIStore } from '../stores/uiStore';
import { PageHeader } from '../components/common/PageHeader';
import { StateWrapper } from '../components/common/StateWrapper';
import { MetricDisplay } from '../components/common/MetricDisplay';
import { ConfidencePill } from '../components/common/ConfidencePill';
import { TimeModelChart } from '../components/visualizations/TimeModelChart';
import { StatusChip } from '../components/common/StatusChip';
import { Activity, Wifi, Clock, AlertTriangle, ShieldCheck, Fuel, Gauge, Layers } from 'lucide-react';

export const LiveOperationPage: React.FC = () => {
  const { missionId } = useParams<{ missionId?: string }>();
  const globalSelectedId = useUIStore((state) => state.selectedMissionId);
  const openDrawer = useUIStore((state) => state.openEvidenceDrawer);

  const activeId = missionId || globalSelectedId;

  // Real-time Telemetry Stream Hook
  const { status: wsStatus, latestTick } = useWebSocket(activeId);

  // Composite API Query
  const { data: composite, isLoading, isError, refetch } = useQuery({
    queryKey: ['live-operation-composite', activeId],
    queryFn: () => outcomeIQApi.getLiveOperationComposite(activeId),
    refetchInterval: 5000,
  });

  const reality = composite?.reality_engine?.value;
  const timeModel = composite?.time_model?.value;
  const guardian = composite?.outcome_guardian?.value;

  const handleInspectReality = () => {
    if (composite?.reality_engine) {
      openDrawer({
        title: 'Reality Engine Anomaly Explanation',
        confidence: composite.reality_engine.confidence,
        evidence: composite.reality_engine.evidence,
      });
    }
  };

  return (
    <div>
      <PageHeader
        title={`Live Operation Console — ${activeId}`}
        subtitle="Real-time telematics multi-signal reasoning: distinguishes raw metric from true operational cause."
      >
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-xs font-display border ${
              wsStatus === 'connected'
                ? 'bg-status-green/15 text-status-green border-status-green/40'
                : 'bg-accent/15 text-accent border-accent/40'
            }`}
          >
            <Wifi className="w-3.5 h-3.5 animate-pulse" />
            <span>WebSocket: {wsStatus === 'connected' ? 'Live Telemetry' : 'Dev Stream'}</span>
          </span>
        </div>
      </PageHeader>

      <StateWrapper isLoading={isLoading} isError={isError} onRetry={refetch}>
        {composite && (
          <div className="space-y-6">
            {/* Reality Engine Live Anomaly Headline Bar */}
            <div
              onClick={handleInspectReality}
              className={`bg-panel border rounded-md p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer hover:border-accent/40 transition-colors ${
                reality?.explanation_class === 'external_workflow'
                  ? 'border-accent/50 bg-accent/5'
                  : 'border-hairline'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="p-2.5 rounded-sm bg-accent/15 text-accent shrink-0 mt-0.5">
                  <Activity className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-display uppercase tracking-widest text-accent font-semibold">
                      Reality Engine Live Reasoner
                    </span>
                    <span className="text-xs font-mono text-text-muted">
                      Class: {reality?.explanation_class}
                    </span>
                  </div>
                  <h3 className="font-display text-base font-bold text-text-primary">
                    {reality?.headline}
                  </h3>
                  <p className="text-xs font-body text-text-secondary mt-1">
                    Primary Driver: <strong className="text-text-primary font-medium">{reality?.primary_driver}</strong>
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                {composite.reality_engine && (
                  <ConfidencePill
                    confidence={composite.reality_engine.confidence}
                    evidence={composite.reality_engine.evidence}
                    title="Reality Engine Explanation"
                  />
                )}
              </div>
            </div>

            {/* Live Metrics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricDisplay
                label="P50 Live Expected ETA"
                value={timeModel?.p50_min || 0}
                unit="mins"
                subtext={`P10–P90 Range: ${timeModel?.p10_min}–${timeModel?.p90_min} min`}
                confidence={composite.time_model?.confidence}
                evidence={composite.time_model?.evidence}
                color="blue"
                highlight
              />

              <MetricDisplay
                label="Current Idle Time"
                value={latestTick?.idle_minutes ?? 18}
                unit="mins"
                subtext={reality?.workflow_context?.truck_present ? 'Idle normal' : 'Truck queue absent 7 min'}
                color={latestTick?.idle_minutes && latestTick.idle_minutes > 10 ? 'amber' : 'primary'}
              />

              <MetricDisplay
                label="Control Smoothness"
                value={`${latestTick?.control_smoothness_score ?? 91}/100`}
                unit="index"
                subtext="Normal hydraulic modulation"
                color="green"
              />

              <MetricDisplay
                label="Seatbelt & Safety"
                value={latestTick?.seatbelt_status ? '100% OK' : 'Violation'}
                unit="compliance"
                subtext="0 proximity or speed alerts"
                color="green"
              />
            </div>

            {/* Time Model Quantile Chart */}
            {timeModel && <TimeModelChart timeData={timeModel} />}
          </div>
        )}
      </StateWrapper>
    </div>
  );
};

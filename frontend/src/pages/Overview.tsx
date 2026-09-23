import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { outcomeIQApi } from '../services/api';
import { PageHeader } from '../components/common/PageHeader';
import { StateWrapper } from '../components/common/StateWrapper';
import { MetricDisplay } from '../components/common/MetricDisplay';
import { HeroSplineCanvas } from '../components/visualizations/HeroSplineCanvas';
import { MissionCard } from '../components/modules/MissionCard';
import { Layers, Activity, AlertTriangle, ShieldCheck } from 'lucide-react';

export const OverviewPage: React.FC = () => {
  const { data: missions, isLoading, isError, refetch } = useQuery({
    queryKey: ['missions'],
    queryFn: () => outcomeIQApi.getMissions(),
  });

  const activeCount = missions?.length || 0;
  const qualityWatchCount = missions?.filter((m) => m.status === 'quality_alert').length || 0;
  const timeDriftCount = missions?.filter((m) => m.scenario_tag === 'FALSE_IDLE').length || 0;

  return (
    <div>
      <PageHeader
        title="Jobsite Command Console"
        subtitle="Real-time outcome assurance and context-aware reasoning above connected fleet telematics."
      />

      {/* Hero WebGL Jobsite Visualizer */}
      <HeroSplineCanvas className="mb-6" />

      {/* Key Jobsite Outcome Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <MetricDisplay
          label="Active Missions"
          value={activeCount}
          unit="live"
          subtext="Connected excavation, trenching, & subgrade missions."
          color="amber"
          highlight
        />
        <MetricDisplay
          label="Quality Watch Flags"
          value={qualityWatchCount}
          unit="active"
          subtext="Missions on schedule but flagging subgrade elevation variance."
          color={qualityWatchCount > 0 ? 'red' : 'green'}
        />
        <MetricDisplay
          label="Time Drift Alerts"
          value={timeDriftCount}
          unit="detected"
          subtext="Idle spikes classified as external haul truck bottlenecks."
          color={timeDriftCount > 0 ? 'amber' : 'green'}
        />
        <MetricDisplay
          label="Fleet Safety Signal"
          value="100%"
          unit="compliant"
          subtext="0 speed or seatbelt violations recorded in last 24h."
          color="green"
        />
      </div>

      {/* Mission Cards Feed */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-accent" />
            <h2 className="font-display text-base font-semibold text-text-primary">
              Active Jobsite Missions ({activeCount})
            </h2>
          </div>
          <span className="text-xs font-body text-text-muted">
            Select any mission card to open its Live Operation intelligence console.
          </span>
        </div>

        <StateWrapper isLoading={isLoading} isError={isError} onRetry={refetch}>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {missions?.map((mission) => (
              <MissionCard key={mission.id} mission={mission} />
            ))}
          </div>
        </StateWrapper>
      </div>
    </div>
  );
};

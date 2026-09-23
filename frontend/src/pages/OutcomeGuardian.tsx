import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { outcomeIQApi } from '../services/api';
import { useUIStore } from '../stores/uiStore';
import { PageHeader } from '../components/common/PageHeader';
import { StateWrapper } from '../components/common/StateWrapper';
import { MetricDisplay } from '../components/common/MetricDisplay';
import { ConfidencePill } from '../components/common/ConfidencePill';
import { SignalGrid } from '../components/modules/SignalGrid';
import { ElevationTerrainMesh } from '../components/visualizations/ElevationTerrainMesh';
import { ShieldAlert, AlertTriangle, CheckCircle2, Award } from 'lucide-react';

export const OutcomeGuardianPage: React.FC = () => {
  const { missionId } = useParams<{ missionId?: string }>();
  const globalSelectedId = useUIStore((state) => state.selectedMissionId);

  const activeId = missionId || globalSelectedId;

  const { data: guardianEnvelope, isLoading, isError, refetch } = useQuery({
    queryKey: ['outcome-guardian', activeId],
    queryFn: () => outcomeIQApi.getOutcomeGuardian(activeId),
  });

  const guardian = guardianEnvelope?.value;
  const isQualityAlert = guardian?.signals.quality === 'red' || guardian?.signals.quality === 'amber';

  return (
    <div>
      <PageHeader
        title={`Outcome Guardian — ${activeId}`}
        subtitle="Tracks Time, Safety, Productivity, Fuel, Quality, & Acceptance as separate signals. Prevents machine activity from masking outcome failure."
      />

      <StateWrapper isLoading={isLoading} isError={isError} onRetry={refetch}>
        {guardian && (
          <div className="space-y-6">
            {/* Guardian Reveal Banner */}
            <div
              className={`bg-panel border rounded-md p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                isQualityAlert ? 'border-status-red/50 bg-status-red/5' : 'border-hairline'
              }`}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`p-3 rounded-sm shrink-0 ${
                    isQualityAlert ? 'bg-status-red/15 text-status-red' : 'bg-status-green/15 text-status-green'
                  }`}
                >
                  <ShieldAlert className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`text-[10px] font-display uppercase tracking-widest px-2 py-0.5 rounded-sm font-semibold border ${
                        isQualityAlert
                          ? 'bg-status-red/20 text-status-red border-status-red/40'
                          : 'bg-status-green/20 text-status-green border-status-green/40'
                      }`}
                    >
                      {isQualityAlert ? 'Quality Assurance Warning' : 'All Signals Nominal'}
                    </span>
                  </div>
                  <h2 className="font-display text-lg font-bold text-text-primary">
                    {guardian.headline}
                  </h2>
                  <p className="text-xs font-body text-text-secondary mt-1">
                    Predicted Rework Probability:{' '}
                    <strong className="text-text-primary font-medium tabular-nums">
                      {Math.round(guardian.rework_probability * 100)}%
                    </strong>
                  </p>
                </div>
              </div>

              {guardianEnvelope && (
                <ConfidencePill
                  confidence={guardianEnvelope.confidence}
                  evidence={guardianEnvelope.evidence}
                  title="Outcome Guardian Model Confidence"
                />
              )}
            </div>

            {/* 6-Signal Status Grid */}
            <SignalGrid guardianData={guardian} />

            {/* 3D Data-Driven Elevation Terrain Mesh */}
            <ElevationTerrainMesh
              elevationErrorCm={guardian.quality_observation.elevation_error_cm}
              surfaceVariance={guardian.quality_observation.surface_variance}
              isQualityAlert={isQualityAlert}
            />
          </div>
        )}
      </StateWrapper>
    </div>
  );
};

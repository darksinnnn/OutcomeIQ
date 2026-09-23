import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { outcomeIQApi } from '../services/api';
import { useUIStore } from '../stores/uiStore';
import { PageHeader } from '../components/common/PageHeader';
import { StateWrapper } from '../components/common/StateWrapper';
import { MetricDisplay } from '../components/common/MetricDisplay';
import { ConfidencePill } from '../components/common/ConfidencePill';
import { ContributorBarChart } from '../components/visualizations/ContributorBarChart';
import { GitPullRequest, AlertCircle, ShieldCheck } from 'lucide-react';

export const RootCausePage: React.FC = () => {
  const { missionId } = useParams<{ missionId?: string }>();
  const globalSelectedId = useUIStore((state) => state.selectedMissionId);

  const activeId = missionId || globalSelectedId;

  const { data: rootCauseEnvelope, isLoading, isError, refetch } = useQuery({
    queryKey: ['root-cause', activeId],
    queryFn: () => outcomeIQApi.getRootCause(activeId),
  });

  const rootCause = rootCauseEnvelope?.value;

  return (
    <div>
      <PageHeader
        title={`Root-Cause Attribution Engine — ${activeId}`}
        subtitle="When actual duration diverges from predicted, returns ranked contributor probabilities with traceable evidence."
      />

      <StateWrapper isLoading={isLoading} isError={isError} onRetry={refetch}>
        {rootCause && (
          <div className="space-y-6">
            {/* Headline Deviation Banner */}
            <div className="bg-panel border border-hairline rounded-md p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 rounded-sm bg-accent/15 text-accent border border-accent/30 text-xs font-display font-medium">
                    Deviation Analysis Active
                  </span>
                  <span className="text-xs font-mono text-text-muted">
                    Mission ID: {activeId}
                  </span>
                </div>
                <h2 className="font-display text-2xl font-bold text-text-primary">
                  Measured Trajectory Deviation: <span className="text-accent tabular-nums">+{rootCause.deviation_min} minutes</span>
                </h2>
                <p className="text-xs font-body text-text-secondary mt-1">
                  Primary Attributed Cause: <strong className="text-text-primary font-medium">{rootCause.primary_cause}</strong>
                </p>
              </div>

              {rootCauseEnvelope && (
                <ConfidencePill
                  confidence={rootCauseEnvelope.confidence}
                  evidence={rootCauseEnvelope.evidence}
                  title="Root-Cause Attribution Model Confidence"
                />
              )}
            </div>

            {/* Deviation Context Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <MetricDisplay
                label="Duration Variance"
                value={`+${rootCause.deviation_min}`}
                unit="mins"
                subtext="Versus baseline Time Model P50"
                color="amber"
                highlight
              />
              <MetricDisplay
                label="Primary Contributor"
                value={rootCause.contributors[0]?.cause_category.replace('_', ' ') || 'Workflow'}
                unit=""
                subtext={rootCause.contributors[0]?.cause}
                color="blue"
              />
              <MetricDisplay
                label="Attribution Certainty"
                value={`${Math.round((rootCauseEnvelope?.confidence || 0.89) * 100)}%`}
                unit="confidence"
                subtext="Derived from feature probability fusion"
                color="green"
              />
            </div>

            {/* Ranked Contributor Probability Bars */}
            <div className="bg-panel border border-hairline rounded-md p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-hairline pb-3">
                <div className="flex items-center gap-2">
                  <GitPullRequest className="w-5 h-5 text-accent" />
                  <h3 className="font-display font-semibold text-sm text-text-primary">
                    Ranked Contributor Attribution Probabilities
                  </h3>
                </div>
                <span className="text-xs font-body text-text-muted">
                  Click any contributor row to open its traceable evidence factors.
                </span>
              </div>

              <ContributorBarChart contributors={rootCause.contributors} />
            </div>
          </div>
        )}
      </StateWrapper>
    </div>
  );
};

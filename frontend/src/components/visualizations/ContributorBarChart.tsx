import React from 'react';
import { RootCauseContributor } from '../../types';
import { useUIStore } from '../../stores/uiStore';
import { Layers, ChevronRight } from 'lucide-react';

interface ContributorBarChartProps {
  contributors: RootCauseContributor[];
  className?: string;
}

export const ContributorBarChart: React.FC<ContributorBarChartProps> = ({
  contributors,
  className = '',
}) => {
  const openDrawer = useUIStore((state) => state.openEvidenceDrawer);

  const getCategoryBadge = (cat: string) => {
    switch (cat) {
      case 'external_workflow':
        return 'bg-accent/10 text-accent border-accent/30';
      case 'operator_variation':
        return 'bg-data-blue/10 text-data-blue border-data-blue/30';
      case 'weather_condition':
        return 'bg-status-amber/10 text-status-amber border-status-amber/30';
      default:
        return 'bg-hairline text-text-muted border-hairline';
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {contributors.map((item, idx) => {
        const pct = Math.round(item.probability * 100);

        const handleBarClick = () => {
          openDrawer({
            title: `Root Cause: ${item.cause}`,
            confidence: item.probability,
            evidence: [
              {
                factor: item.cause,
                weight_or_probability: item.probability,
                detail: item.evidence,
              },
            ],
          });
        };

        return (
          <div
            key={idx}
            onClick={handleBarClick}
            className="bg-panel border border-hairline rounded-md p-3.5 hover:border-accent/40 cursor-pointer transition-all duration-150 group"
          >
            <div className="flex items-center justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-text-muted">#{idx + 1}</span>
                <span className="font-display text-xs font-semibold text-text-primary group-hover:text-accent transition-colors">
                  {item.cause}
                </span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-sm border font-display ${getCategoryBadge(
                    item.cause_category
                  )}`}
                >
                  {item.cause_category.replace('_', ' ')}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-display font-semibold text-sm text-text-primary tabular-nums">
                  {pct}%
                </span>
                <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-accent group-hover:translate-x-0.5 transition-all" />
              </div>
            </div>

            {/* Probability Fill Bar */}
            <div className="w-full bg-hairline h-2 rounded-full overflow-hidden">
              <div
                className="bg-accent h-full transition-all duration-300"
                style={{ width: `${pct}%` }}
              />
            </div>

            <p className="text-[11px] font-body text-text-secondary mt-2 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-text-muted shrink-0" />
              <span>{item.evidence}</span>
            </p>
          </div>
        );
      })}
    </div>
  );
};

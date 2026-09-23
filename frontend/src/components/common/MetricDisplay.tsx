import React from 'react';
import { ConfidencePill } from './ConfidencePill';
import { EvidenceFactor } from '../../types';

interface MetricDisplayProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  confidence?: number;
  evidence?: EvidenceFactor[];
  highlight?: boolean;
  color?: 'primary' | 'blue' | 'amber' | 'green' | 'red';
  className?: string;
}

export const MetricDisplay: React.FC<MetricDisplayProps> = ({
  label,
  value,
  unit,
  subtext,
  confidence,
  evidence,
  highlight = false,
  color = 'primary',
  className = '',
}) => {
  const getColorClass = () => {
    switch (color) {
      case 'blue':
        return 'text-data-blue';
      case 'amber':
        return 'text-accent';
      case 'green':
        return 'text-status-green';
      case 'red':
        return 'text-status-red';
      default:
        return 'text-text-primary';
    }
  };

  return (
    <div
      className={`bg-panel border border-hairline rounded-md p-4 flex flex-col justify-between transition-colors ${
        highlight ? 'border-accent/40 bg-elevated' : ''
      } ${className}`}
    >
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <span className="text-text-secondary text-xs font-body font-medium uppercase tracking-wider">
          {label}
        </span>
        {confidence !== undefined && (
          <ConfidencePill confidence={confidence} evidence={evidence} title={label} />
        )}
      </div>

      <div className="flex items-baseline gap-1.5 my-1">
        <span className={`font-display text-2xl font-semibold tabular-nums ${getColorClass()}`}>
          {value}
        </span>
        {unit && <span className="text-text-muted text-sm font-body">{unit}</span>}
      </div>

      {subtext && (
        <p className="text-text-muted text-xs font-body mt-1 leading-relaxed">
          {subtext}
        </p>
      )}
    </div>
  );
};

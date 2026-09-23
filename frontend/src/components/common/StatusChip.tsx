import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { SignalState } from '../../types';

interface StatusChipProps {
  state: SignalState;
  label?: string;
  size?: 'sm' | 'md';
  className?: string;
}

export const StatusChip: React.FC<StatusChipProps> = ({
  state,
  label,
  size = 'md',
  className = '',
}) => {
  const getBadgeStyle = () => {
    switch (state) {
      case 'green':
        return {
          bg: 'bg-status-green/15 text-status-green border-status-green/40',
          icon: CheckCircle2,
          defaultLabel: 'On Track',
        };
      case 'amber':
        return {
          bg: 'bg-status-amber/15 text-status-amber border-status-amber/40',
          icon: AlertTriangle,
          defaultLabel: 'Watch / Risk',
        };
      case 'red':
        return {
          bg: 'bg-status-red/15 text-status-red border-status-red/40',
          icon: XCircle,
          defaultLabel: 'Critical / Failure',
        };
    }
  };

  const config = getBadgeStyle();
  const IconComponent = config.icon;
  const displayText = label || config.defaultLabel;
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs';
  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-display font-medium rounded-sm border ${sizeClasses} ${config.bg} ${className}`}
    >
      <IconComponent className={iconSize} />
      <span>{displayText}</span>
    </span>
  );
};

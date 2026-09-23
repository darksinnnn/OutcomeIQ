import React from 'react';
import { OutcomeGuardianValue } from '../../types';
import { StatusChip } from '../common/StatusChip';
import { Clock, Shield, Gauge, Fuel, Award, CheckSquare } from 'lucide-react';

interface SignalGridProps {
  guardianData: OutcomeGuardianValue;
  className?: string;
}

export const SignalGrid: React.FC<SignalGridProps> = ({ guardianData, className = '' }) => {
  const { signals } = guardianData;

  const SIGNAL_ITEMS = [
    { key: 'time', label: 'Time & Schedule', state: signals.time, icon: Clock, desc: 'P50 duration trajectory alignment' },
    { key: 'safety', label: 'Safety Compliance', state: signals.safety, icon: Shield, desc: 'Seatbelt, speed, & proximity rules' },
    { key: 'productivity', label: 'Productivity Rate', state: signals.productivity, icon: Gauge, desc: 'Load cycle rate & bucket fill efficiency' },
    { key: 'fuel', label: 'Fuel Efficiency', state: signals.fuel, icon: Fuel, desc: 'Liters per completed m3 / ton' },
    { key: 'quality', label: 'Quality Tolerance', state: signals.quality, icon: Award, desc: 'Subgrade elevation & surface variance' },
    { key: 'acceptance', label: 'Outcome Acceptance', state: signals.acceptance, icon: CheckSquare, desc: 'Predicted rework probability' },
  ];

  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`}>
      {SIGNAL_ITEMS.map((item) => {
        const IconComponent = item.icon;
        const isRed = item.state === 'red';
        const isAmber = item.state === 'amber';

        return (
          <div
            key={item.key}
            className={`bg-panel border rounded-md p-4 flex flex-col justify-between transition-all ${
              isRed
                ? 'border-status-red/50 bg-status-red/5'
                : isAmber
                ? 'border-status-amber/40 bg-status-amber/5'
                : 'border-hairline'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <IconComponent className="w-4 h-4 text-text-muted" />
                  <span className="font-display font-medium text-xs text-text-primary">
                    {item.label}
                  </span>
                </div>
                <StatusChip state={item.state} size="sm" />
              </div>

              <p className="text-[11px] font-body text-text-muted mt-1 leading-relaxed">
                {item.desc}
              </p>
            </div>

            {item.key === 'quality' && (
              <div className="mt-3 pt-2 border-t border-hairline/60 flex items-center justify-between text-xs font-mono">
                <span className="text-text-muted">Elevation Error:</span>
                <span className={isRed ? 'text-status-red font-bold' : 'text-text-primary'}>
                  +{guardianData.quality_observation.elevation_error_cm} cm
                </span>
              </div>
            )}

            {item.key === 'acceptance' && (
              <div className="mt-3 pt-2 border-t border-hairline/60 flex items-center justify-between text-xs font-mono">
                <span className="text-text-muted">Rework Risk:</span>
                <span className={isRed || isAmber ? 'text-status-amber font-bold' : 'text-status-green'}>
                  {Math.round(guardianData.rework_probability * 100)}%
                </span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { TimeModelValue } from '../../types';

interface TimeModelChartProps {
  timeData: TimeModelValue;
  className?: string;
}

export const TimeModelChart: React.FC<TimeModelChartProps> = ({ timeData, className = '' }) => {
  // Generate curve points representing duration progress across quantiles
  const chartData = [
    { progress: 'Start (0%)', p10: 0, p50: 0, p90: 0, band: [0, 0] },
    { progress: '25% Load', p10: Math.round(timeData.p10_min * 0.25), p50: Math.round(timeData.p50_min * 0.25), p90: Math.round(timeData.p90_min * 0.25), band: [Math.round(timeData.p10_min * 0.25), Math.round(timeData.p90_min * 0.25)] },
    { progress: '50% Mid', p10: Math.round(timeData.p10_min * 0.5), p50: Math.round(timeData.p50_min * 0.5), p90: Math.round(timeData.p90_min * 0.5), band: [Math.round(timeData.p10_min * 0.5), Math.round(timeData.p90_min * 0.5)] },
    { progress: '75% Finish', p10: Math.round(timeData.p10_min * 0.75), p50: Math.round(timeData.p50_min * 0.75), p90: Math.round(timeData.p90_min * 0.75), band: [Math.round(timeData.p10_min * 0.75), Math.round(timeData.p90_min * 0.75)] },
    { progress: 'Completion', p10: timeData.p10_min, p50: timeData.p50_min, p90: timeData.p90_min, band: [timeData.p10_min, timeData.p90_min] },
  ];

  return (
    <div className={`bg-panel border border-hairline rounded-md p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="font-display font-medium text-xs text-text-primary uppercase tracking-wider">
            Time Model — Quantile Duration Prediction (P10 / P50 / P90)
          </h4>
          <p className="text-[11px] font-body text-text-muted mt-0.5">
            Uncertainty-aware distribution curve based on operator evidence, machine health, and workflow features.
          </p>
        </div>
        <div className="flex items-center gap-3 text-[11px] font-display">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-data-blue inline-block" />
            <span className="text-text-secondary">P50 Expected ({timeData.p50_min} min)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-2 bg-data-blue/30 border border-data-blue inline-block" />
            <span className="text-text-muted">P10–P90 Range ({timeData.p10_min}–{timeData.p90_min} min)</span>
          </div>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2C3238" vertical={false} />
            <XAxis dataKey="progress" stroke="#6B747C" fontSize={11} tickLine={false} />
            <YAxis stroke="#6B747C" fontSize={11} tickLine={false} unit="m" />
            <Tooltip
              contentStyle={{ backgroundColor: '#22272C', borderColor: '#2C3238', borderRadius: '4px', fontSize: '12px' }}
              labelStyle={{ color: '#EDEFF1', fontFamily: 'Space Grotesk' }}
            />
            {/* P10 - P90 Uncertainty Band */}
            <Area
              type="monotone"
              dataKey="band"
              stroke="#5B8DEF"
              strokeDasharray="4 4"
              fill="#5B8DEF"
              fillOpacity={0.18}
              name="P10-P90 Uncertainty Band"
            />
            {/* P50 Expected Median Line */}
            <Line
              type="monotone"
              dataKey="p50"
              stroke="#5B8DEF"
              strokeWidth={2.5}
              dot={{ fill: '#5B8DEF', r: 4 }}
              name="P50 Expected Duration"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

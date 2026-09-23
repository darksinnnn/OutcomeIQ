import React from 'react';
import { motion } from 'framer-motion';
import { WhatIfValue } from '../../types';
import { Clock, Fuel, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { ConfidencePill } from '../common/ConfidencePill';

interface BeforeAfterComparisonProps {
  whatIfData: WhatIfValue;
  confidence: number;
  evidence: any[];
}

export const BeforeAfterComparison: React.FC<BeforeAfterComparisonProps> = ({
  whatIfData,
  confidence,
  evidence,
}) => {
  const { before, after, time_delta_min, fuel_delta_l } = whatIfData;

  const isTimeSaved = time_delta_min < 0;
  const isFuelSaved = fuel_delta_l < 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="bg-panel border border-accent/40 rounded-md p-6 space-y-6"
    >
      {/* Simulation Header & Assumption Label */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-hairline pb-4">
        <div>
          <span className="text-[10px] font-display uppercase tracking-widest px-2 py-0.5 rounded-sm bg-accent/15 text-accent border border-accent/30 font-medium">
            Simulated What-If Intervention Result
          </span>
          <h3 className="font-display text-base font-semibold text-text-primary mt-1.5">
            {whatIfData.description}
          </h3>
        </div>
        <ConfidencePill confidence={confidence} evidence={evidence} title="What-If Simulation Confidence" />
      </div>

      {/* Before vs After Metric Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Baseline (Before) State */}
        <div className="bg-base/60 border border-hairline rounded-md p-4 space-y-3">
          <div className="flex items-center justify-between text-xs font-display text-text-muted">
            <span className="uppercase tracking-wider font-semibold">Baseline Trajectory (Before)</span>
            <span className="px-2 py-0.5 rounded-sm bg-hairline text-text-muted font-mono">Current State</span>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-body text-text-secondary flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-text-muted" /> Expected P50 Duration:
              </span>
              <span className="font-display text-sm font-semibold text-text-primary tabular-nums">
                {before.p50_min} mins
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-body text-text-secondary flex items-center gap-1.5">
                <Fuel className="w-3.5 h-3.5 text-text-muted" /> Expected Fuel Burn:
              </span>
              <span className="font-display text-sm font-semibold text-text-primary tabular-nums">
                {before.expected_fuel_l} L
              </span>
            </div>
          </div>
        </div>

        {/* Simulated (After) State */}
        <div className="bg-elevated border border-data-blue/40 rounded-md p-4 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs font-display text-data-blue">
            <span className="uppercase tracking-wider font-semibold">Intervention Trajectory (After)</span>
            <span className="px-2 py-0.5 rounded-sm bg-data-blue/15 text-data-blue border border-data-blue/30 font-mono">
              Simulated Result
            </span>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-body text-text-secondary flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-data-blue" /> Expected P50 Duration:
              </span>
              <span className="font-display text-sm font-semibold text-data-blue tabular-nums">
                {after.p50_min} mins
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-body text-text-secondary flex items-center gap-1.5">
                <Fuel className="w-3.5 h-3.5 text-data-blue" /> Expected Fuel Burn:
              </span>
              <span className="font-display text-sm font-semibold text-data-blue tabular-nums">
                {after.expected_fuel_l} L
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Net Impact Delta Highlights */}
      <div className="bg-base border border-hairline rounded-md p-4 flex flex-col sm:flex-row items-center justify-around gap-4 text-center">
        <div className="flex items-center gap-3">
          <div className={`w-9 h-9 rounded-sm flex items-center justify-center ${isTimeSaved ? 'bg-status-green/15 text-status-green' : 'bg-status-amber/15 text-status-amber'}`}>
            <Clock className="w-5 h-5" />
          </div>
          <div className="text-left">
            <span className="text-[10px] font-display uppercase tracking-wider text-text-muted block">
              Schedule Delta
            </span>
            <span className={`font-display text-base font-bold tabular-nums ${isTimeSaved ? 'text-status-green' : 'text-status-amber'}`}>
              {time_delta_min} mins {isTimeSaved ? 'Faster' : 'Slower'}
            </span>
          </div>
        </div>

        <div className="h-8 w-px bg-hairline hidden sm:block" />

        <div className="flex items-center gap-3">
          <div className={`w-9 h-9 rounded-sm flex items-center justify-center ${isFuelSaved ? 'bg-status-green/15 text-status-green' : 'bg-status-amber/15 text-status-amber'}`}>
            <Fuel className="w-5 h-5" />
          </div>
          <div className="text-left">
            <span className="text-[10px] font-display uppercase tracking-wider text-text-muted block">
              Fuel Burn Delta
            </span>
            <span className={`font-display text-base font-bold tabular-nums ${isFuelSaved ? 'text-status-green' : 'text-status-amber'}`}>
              {fuel_delta_l} L {isFuelSaved ? 'Saved' : 'Increase'}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

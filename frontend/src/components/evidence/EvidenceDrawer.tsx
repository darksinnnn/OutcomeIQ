import React from 'react';
import { useUIStore } from '../../stores/uiStore';
import { ShieldCheck, X, FileText, CheckCircle, Info } from 'lucide-react';
import { ConfidencePill } from '../common/ConfidencePill';

export const EvidenceDrawer: React.FC = () => {
  const isDrawerOpen = useUIStore((state) => state.isDrawerOpen);
  const drawerData = useUIStore((state) => state.drawerData);
  const closeDrawer = useUIStore((state) => state.closeEvidenceDrawer);

  if (!isDrawerOpen || !drawerData) return null;

  const pct = Math.round(drawerData.confidence * 100);

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-elevated border-l border-hairline shadow-elevated flex flex-col transition-transform duration-200 ease-out">
      {/* Drawer Header */}
      <div className="p-4 border-b border-hairline flex items-center justify-between bg-panel">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-accent" />
          <div>
            <h3 className="font-display font-semibold text-sm text-text-primary">
              Prediction Evidence Trace
            </h3>
            <p className="text-[11px] font-body text-text-muted">
              {drawerData.title}
            </p>
          </div>
        </div>
        <button
          onClick={closeDrawer}
          className="p-1 rounded-sm text-text-muted hover:text-text-primary hover:bg-hairline transition-colors"
          title="Close drawer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Drawer Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {/* Confidence Summary */}
        <div className="bg-panel p-4 rounded-md border border-hairline">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-display text-text-secondary uppercase">
              Model Confidence
            </span>
            <ConfidencePill confidence={drawerData.confidence} />
          </div>
          <div className="w-full bg-hairline h-2 rounded-full overflow-hidden">
            <div
              className="bg-accent h-full transition-all duration-300"
              style={{ width: `${pct}%` }}
            />
          </div>
          <p className="text-[11px] text-text-muted font-body mt-2 leading-relaxed">
            Confidence score reflects model uncertainty evaluated against historical context-specific evidence and feature alignment.
          </p>
        </div>

        {/* Contributing Evidence Factors */}
        <div>
          <h4 className="text-xs font-display uppercase tracking-wider text-text-secondary mb-3 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-accent" />
            Contributing Evidence Factors ({drawerData.evidence.length})
          </h4>

          {drawerData.evidence.length === 0 ? (
            <p className="text-xs text-text-muted italic">No evidence details attached to this readout.</p>
          ) : (
            <div className="space-y-3">
              {drawerData.evidence.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-panel border border-hairline rounded-md p-3 text-xs space-y-1.5 hover:border-accent/30 transition-colors"
                >
                  <div className="flex items-center justify-between font-display text-text-primary font-medium">
                    <span className="flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-accent" />
                      {item.factor}
                    </span>
                    <span className="text-accent font-mono text-[11px]">
                      {Math.round(item.weight_or_probability * 100)}% weight
                    </span>
                  </div>
                  <p className="text-text-secondary font-body leading-relaxed pl-5">
                    {item.detail}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Trust & Safety Assurance */}
        <div className="bg-panel/60 border border-hairline p-3 rounded-md flex items-start gap-2.5">
          <Info className="w-4 h-4 text-data-blue shrink-0 mt-0.5" />
          <p className="text-[11px] text-text-muted font-body leading-relaxed">
            <strong className="text-text-secondary font-medium">Trust & Safety Contract:</strong> Every factor is traceable back to recorded telematics, environment sensors, or operator evidence. No unsupported claims or arbitrary scoring.
          </p>
        </div>
      </div>

      {/* Drawer Footer */}
      <div className="p-3 border-t border-hairline bg-panel text-center">
        <button
          onClick={closeDrawer}
          className="w-full py-1.5 bg-elevated hover:bg-hairline text-text-primary text-xs font-display font-medium rounded-sm border border-hairline transition-colors"
        >
          Close Panel
        </button>
      </div>
    </div>
  );
};

import React from 'react';
import { ShieldCheck, HelpCircle } from 'lucide-react';
import { useUIStore } from '../../stores/uiStore';
import { EvidenceFactor } from '../../types';

interface ConfidencePillProps {
  confidence: number; // 0.0 - 1.0
  evidence?: EvidenceFactor[];
  title?: string;
  className?: string;
}

export const ConfidencePill: React.FC<ConfidencePillProps> = ({
  confidence,
  evidence = [],
  title = 'Prediction Confidence',
  className = '',
}) => {
  const openDrawer = useUIStore((state) => state.openEvidenceDrawer);
  const pct = Math.round(confidence * 100);

  const getStyle = () => {
    if (pct >= 85) return 'bg-accent/10 text-accent border-accent/30 hover:bg-accent/20';
    if (pct >= 70) return 'bg-status-amber/10 text-status-amber border-status-amber/30 hover:bg-status-amber/20';
    return 'bg-status-red/10 text-status-red border-status-red/30 hover:bg-status-red/20';
  };

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    openDrawer({
      title,
      confidence,
      evidence,
    });
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      title="Click to view traceable evidence factors"
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-sm text-xs font-display font-medium border border-hairline transition-all duration-150 focus:ring-2 focus:ring-accent ${getStyle()} ${className}`}
    >
      <ShieldCheck className="w-3.5 h-3.5" />
      <span>{pct}% Confidence</span>
      {evidence.length > 0 && (
        <span className="text-[10px] opacity-75 font-body">({evidence.length} factors)</span>
      )}
      <HelpCircle className="w-3 h-3 ml-0.5 opacity-60" />
    </button>
  );
};

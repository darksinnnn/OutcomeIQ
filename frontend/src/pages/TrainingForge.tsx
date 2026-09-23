import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { GraduationCap, Compass, Layers } from 'lucide-react';

export const TrainingForgePage: React.FC = () => {
  return (
    <div>
      <PageHeader
        title="Training Forge — Contextual Skill Module"
        subtitle="Generates micro-coaching scenarios targeted specifically at observed Operator Passport context gaps."
        badgeText="Roadmap Vision Mock"
      />

      <div className="bg-panel border border-hairline rounded-md p-8 text-center space-y-4 max-w-2xl mx-auto my-12">
        <div className="w-16 h-16 rounded-full bg-accent/15 text-accent flex items-center justify-center mx-auto border border-accent/30">
          <GraduationCap className="w-8 h-8" />
        </div>
        <div>
          <span className="text-[10px] font-display uppercase tracking-widest px-2.5 py-1 rounded-sm bg-hairline text-text-muted border border-hairline font-semibold">
            Roadmap Concept — Phase 2 Architecture
          </span>
          <h2 className="font-display text-xl font-bold text-text-primary mt-3">
            Contextual Training Forge Engine
          </h2>
          <p className="text-xs font-body text-text-secondary mt-2 leading-relaxed">
            Unlike generic video safety libraries, Training Forge automatically triggers contextual simulations when Operator Passport evidence flags an unfamiliar material/moisture combination (e.g. wet clay trenching).
          </p>
        </div>

        <div className="pt-4 border-t border-hairline grid grid-cols-1 sm:grid-cols-2 gap-4 text-left text-xs font-body">
          <div className="bg-base p-3 rounded-sm border border-hairline">
            <span className="font-display font-semibold text-text-primary block mb-1">Triggering Context</span>
            <span className="text-text-muted">Wet Clay & Silt Trenching (4 sample missions, 58% confidence)</span>
          </div>
          <div className="bg-base p-3 rounded-sm border border-hairline">
            <span className="font-display font-semibold text-accent block mb-1">Generated Simulator</span>
            <span className="text-text-muted">Joystick hydraulic bucket curl modulation in high-adhesion clay</span>
          </div>
        </div>
      </div>
    </div>
  );
};

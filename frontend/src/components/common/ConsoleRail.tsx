import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileCheck2,
  Activity,
  GitPullRequest,
  ShieldAlert,
  FlaskConical,
  UserCheck,
  GraduationCap,
  BrainCircuit,
  Compass,
  Zap,
} from 'lucide-react';

interface NavItem {
  to: string;
  label: string;
  icon: React.ElementType;
  badge?: string;
  isCore?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, isCore: true },
  { to: '/missions', label: 'Mission Center', icon: FileCheck2, isCore: true },
  { to: '/live', label: 'Live Operation', icon: Activity, badge: 'WS', isCore: true },
  { to: '/root-cause', label: 'Root Cause', icon: GitPullRequest, isCore: true },
  { to: '/outcome-guardian', label: 'Outcome Guardian', icon: ShieldAlert, isCore: true },
  { to: '/what-if', label: 'What-If Lab', icon: FlaskConical, isCore: true },
  { to: '/operators', label: 'Operator Passport', icon: UserCheck, isCore: true },
  // Vision / Stretch Roadmap Mocks
  { to: '/training-forge', label: 'Training Forge', icon: GraduationCap, badge: 'Roadmap' },
  { to: '/operational-memory', label: 'Operational Memory', icon: BrainCircuit, badge: 'Roadmap' },
  { to: '/site-stability', label: 'Site Stability', icon: Compass, badge: 'Roadmap' },
];

export const ConsoleRail: React.FC = () => {
  return (
    <aside className="w-16 tablet:w-64 bg-panel border-r border-hairline flex flex-col h-screen sticky top-0 shrink-0 select-none z-30">
      {/* Brand Header */}
      <div className="p-4 border-b border-hairline flex items-center gap-3">
        <div className="w-8 h-8 rounded-sm bg-accent text-base font-display font-bold flex items-center justify-center shrink-0 shadow-sm">
          <Zap className="w-5 h-5 fill-base" />
        </div>
        <div className="hidden tablet:block overflow-hidden">
          <h2 className="font-display font-bold text-sm tracking-tight text-text-primary uppercase">
            CAT OutcomeIQ
          </h2>
          <p className="text-[10px] text-text-muted font-body truncate">
            Mission Intelligence Console
          </p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-1">
        <div className="hidden tablet:block px-2 pb-1 text-[10px] font-display uppercase tracking-wider text-text-muted font-semibold">
          Core Reasoning Modules
        </div>

        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-sm text-xs font-display font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-accent/15 text-text-primary border-l-2 border-accent text-accent'
                    : 'text-text-secondary hover:text-text-primary hover:bg-elevated'
                }`
              }
              title={item.label}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="hidden tablet:inline truncate flex-1">{item.label}</span>
              {item.badge && (
                <span className="hidden tablet:inline-block text-[9px] px-1.5 py-0.2 rounded-sm bg-elevated text-text-muted border border-hairline font-mono">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Rail Footer */}
      <div className="p-3 border-t border-hairline bg-elevated/50 text-[11px] font-body text-text-muted text-center tablet:text-left">
        <div className="hidden tablet:flex items-center justify-between">
          <span className="font-display text-[10px] text-accent uppercase">System Online</span>
          <span className="font-mono text-[10px]">v1.0.0</span>
        </div>
        <div className="tablet:hidden flex justify-center">
          <div className="w-2 h-2 rounded-full bg-status-green animate-pulse" />
        </div>
      </div>
    </aside>
  );
};

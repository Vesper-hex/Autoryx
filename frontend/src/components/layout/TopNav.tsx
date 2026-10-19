import React from 'react';
import { GitBranch, Plus, ShieldCheck, CheckCircle2, AlertTriangle } from 'lucide-react';
import { NavTab } from './Sidebar';

interface TopNavProps {
  currentTab: NavTab;
  onNewAssignment: () => void;
  branchName?: string;
  githubConnected: boolean;
}

export const TopNav: React.FC<TopNavProps> = ({
  currentTab,
  onNewAssignment,
  branchName = 'main',
  githubConnected,
}) => {
  const getTitle = () => {
    switch (currentTab) {
      case 'dashboard':
        return 'Overview Dashboard';
      case 'new-assignment':
        return 'New Assignment Intake';
      case 'history':
        return 'Assignment History';
      case 'repository':
        return 'GitHub Repository Explorer';
      case 'activity':
        return 'Live System Activity Logs';
      case 'settings':
        return 'Settings & Configuration';
      case 'workspace':
        return 'Assignment Automation Workspace';
      default:
        return 'Dashboard';
    }
  };

  return (
    <header className="h-16 border-b border-border-subtle bg-dark-900/60 backdrop-blur px-6 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <h1 className="text-base font-semibold text-slate-100">{getTitle()}</h1>
        <div className="h-4 w-[1px] bg-border-subtle mx-1" />
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-dark-850 border border-border-subtle text-xs font-mono text-slate-300">
          <GitBranch size={13} className="text-accent-cyan" />
          <span>{branchName}</span>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-dark-850 border border-border-subtle text-xs text-slate-300">
          <ShieldCheck size={13} className="text-accent-violet" />
          <span className="font-mono text-[11px]">Strict Isolation Mode</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-lg bg-dark-850 border border-border-subtle">
          {githubConnected ? (
            <>
              <CheckCircle2 size={14} className="text-emerald-400" />
              <span className="text-slate-300 font-mono text-xs">GitHub Connected</span>
            </>
          ) : (
            <>
              <AlertTriangle size={14} className="text-amber-400" />
              <span className="text-amber-300 text-xs">Token Unset</span>
            </>
          )}
        </div>

        {currentTab !== 'new-assignment' && (
          <button
            onClick={onNewAssignment}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-accent-violet to-accent-cyan hover:opacity-95 text-white text-xs font-semibold shadow-sm transition-all"
          >
            <Plus size={15} />
            <span>New Assignment</span>
          </button>
        )}
      </div>
    </header>
  );
};

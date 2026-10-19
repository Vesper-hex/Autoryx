import React from 'react';
import {
  LayoutDashboard,
  PlusCircle,
  History,
  FolderGit2,
  Activity,
  Settings as SettingsIcon,
  Cpu,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';

export type NavTab = 'dashboard' | 'new-assignment' | 'history' | 'repository' | 'activity' | 'settings' | 'workspace';

interface SidebarProps {
  currentTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  workerRunning: boolean;
  repoName: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onTabChange,
  workerRunning,
  repoName,
}) => {
  const navItems: { id: NavTab; label: string; icon: React.ReactNode; badge?: string }[] = [
    { id: 'dashboard', label: 'Overview', icon: <LayoutDashboard size={18} /> },
    { id: 'new-assignment', label: 'New Assignment', icon: <PlusCircle size={18} /> },
    { id: 'history', label: 'Assignment History', icon: <History size={18} /> },
    { id: 'repository', label: 'Repository', icon: <FolderGit2 size={18} /> },
    { id: 'activity', label: 'Activity Logs', icon: <Activity size={18} /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon size={18} /> },
  ];

  return (
    <aside className="w-64 bg-dark-900 border-r border-border-subtle flex flex-col justify-between shrink-0 h-full select-none">
      {/* Brand & Logo Header */}
      <div>
        <div className="h-16 flex items-center gap-3 px-5 border-b border-border-subtle">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-violet to-accent-cyan flex items-center justify-center shadow-lg shadow-accent-violet/20">
            <Cpu size={20} className="text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-base tracking-wide text-white">AUTORYX</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-accent-violet/20 text-accent-violet font-semibold">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium truncate">Your Assignment. Automated.</p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-1.5 text-[10px] font-semibold tracking-wider text-slate-400 uppercase font-mono">
            Automation Suite
          </div>
          {navItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-accent-violet/15 text-accent-cyan border border-accent-violet/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-dark-850'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={isActive ? 'text-accent-cyan' : 'text-slate-400'}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-dark-800 text-slate-300 border border-border-subtle">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Target Repo & Worker Health Status */}
      <div className="p-4 border-t border-border-subtle space-y-3">
        <div className="bg-dark-850 rounded-lg p-3 border border-border-subtle">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-mono text-slate-400 uppercase">Target Repository</span>
            <a
              href="https://github.com/Highorder-Thinking/Step_semester_3"
              target="_blank"
              rel="noreferrer"
              className="text-slate-400 hover:text-accent-cyan transition-colors"
            >
              <ExternalLink size={12} />
            </a>
          </div>
          <p className="text-xs font-mono font-medium text-slate-200 truncate">{repoName || 'Step_semester_3'}</p>
          <div className="mt-2 flex items-center gap-1.5 text-[11px] text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Path: <code className="text-[10px] text-accent-cyan font-mono">STEP_Agent_Assignments/</code></span>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs px-1 text-slate-400">
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${workerRunning ? 'bg-emerald-400 animate-pulse-subtle' : 'bg-amber-400'}`} />
            <span>Worker: {workerRunning ? 'Active (Queue)' : 'Idle'}</span>
          </div>
          <span className="font-mono text-[11px] text-slate-400">Cloud Ready</span>
        </div>
      </div>
    </aside>
  );
};

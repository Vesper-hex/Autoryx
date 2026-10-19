import React from 'react';
import {
  FileCode2,
  FolderCheck,
  AlertCircle,
  GitCommit,
  ArrowRight,
  Upload,
  Cpu,
  Clock,
  Sparkles,
} from 'lucide-react';
import { Assignment, ActivityLog, Job } from '../../lib/types';

interface DashboardViewProps {
  assignments: Assignment[];
  activities: ActivityLog[];
  onNewAssignment: () => void;
  onSelectAssignment: (id: string) => void;
  repoOwner: string;
  repoName: string;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  assignments,
  activities,
  onNewAssignment,
  onSelectAssignment,
  repoOwner,
  repoName,
}) => {
  const totalAssignments = assignments.length;
  const totalQuestions = assignments.reduce((acc, a) => acc + (a.questions?.length || 0), 0);
  const readyOrPublished = assignments.filter((a) => a.status === 'ready_to_publish' || a.status === 'published').length;
  const passRate = totalAssignments > 0 ? Math.round((readyOrPublished / totalAssignments) * 100) : 100;

  return (
    <div className="p-8 space-y-8 overflow-y-auto h-full max-w-7xl mx-auto">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-dark-850 via-dark-800 to-dark-850 p-6 border border-border-default shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent-violet/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1.5">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-accent-violet/15 border border-accent-violet/30 text-accent-cyan text-xs font-mono">
              <Sparkles size={13} />
              <span>AI STEP Assignment Automation</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">
              Welcome to <span className="bg-gradient-to-r from-accent-violet to-accent-cyan bg-clip-text text-transparent">Autoryx</span>
            </h2>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              Automated programming assignment intake, multi-question extraction, sandbox compilation,
              sample test validation, automated repairs, and verified GitHub publishing to{' '}
              <code className="px-1.5 py-0.5 rounded bg-dark-950 font-mono text-accent-cyan text-xs">
                {repoOwner}/{repoName}
              </code>.
            </p>
          </div>
          <button
            onClick={onNewAssignment}
            className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-accent-violet to-accent-cyan text-white text-sm font-semibold shadow-lg shadow-accent-violet/25 hover:opacity-95 transition-all shrink-0"
          >
            <Upload size={16} />
            <span>Process Assignment</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-dark-900 border border-border-subtle rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Assignments</span>
            <FileCode2 size={18} className="text-accent-violet" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{totalAssignments}</div>
          <p className="text-xs text-slate-400">Total received assignments</p>
        </div>

        <div className="bg-dark-900 border border-border-subtle rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Questions Solved</span>
            <FolderCheck size={18} className="text-accent-cyan" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{totalQuestions}</div>
          <p className="text-xs text-slate-400">Extracted and coded problems</p>
        </div>

        <div className="bg-dark-900 border border-border-subtle rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Validation Pass</span>
            <CheckCircleIcon size={18} className="text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{passRate}%</div>
          <p className="text-xs text-slate-400">Passed sandboxed tests</p>
        </div>

        <div className="bg-dark-900 border border-border-subtle rounded-xl p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Target Folder</span>
            <GitCommit size={18} className="text-indigo-400" />
          </div>
          <div className="text-xs font-bold text-accent-cyan font-mono truncate mt-1">STEP_Agent_Assignments/</div>
          <p className="text-xs text-slate-400">Strictly isolated</p>
        </div>
      </div>

      {/* Main Grid: Recent Assignments & Live Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Assignments Table */}
        <div className="lg:col-span-2 bg-dark-900 border border-border-subtle rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-white">Recent Assignments</h3>
              <p className="text-xs text-slate-400">Manage and monitor assignment automation jobs</p>
            </div>
            <button
              onClick={onNewAssignment}
              className="text-xs text-accent-cyan hover:underline font-medium"
            >
              + Intake New
            </button>
          </div>

          {assignments.length === 0 ? (
            <div className="py-12 text-center space-y-3 border border-dashed border-border-subtle rounded-xl">
              <Cpu size={32} className="mx-auto text-slate-600" />
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-300">No assignments processed yet</p>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Upload a PDF assignment or paste questions to start automated question extraction and code generation.
                </p>
              </div>
              <button
                onClick={onNewAssignment}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-dark-800 border border-border-default text-xs font-medium text-slate-200 hover:text-white hover:bg-dark-750"
              >
                <span>Upload First Assignment</span>
                <ArrowRight size={13} />
              </button>
            </div>
          ) : (
            <div className="divide-y divide-border-subtle">
              {assignments.slice(0, 5).map((a) => (
                <div
                  key={a.id}
                  onClick={() => onSelectAssignment(a.id)}
                  className="py-3.5 flex items-center justify-between hover:bg-dark-850 px-2 rounded-lg cursor-pointer transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-200">{a.title}</span>
                      {a.week_module && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-dark-800 border border-border-subtle text-slate-400">
                          {a.week_module}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span className="uppercase font-mono text-[11px] text-accent-cyan font-semibold">
                        {a.language}
                      </span>
                      <span>•</span>
                      <span>{a.questions?.length || 0} question(s)</span>
                      <span>•</span>
                      <span>{new Date(a.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`text-[11px] font-mono px-2.5 py-1 rounded-full uppercase font-medium ${
                        a.status === 'published'
                          ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40'
                          : a.status === 'ready_to_publish'
                          ? 'bg-sky-950/60 text-sky-400 border border-sky-800/40'
                          : a.status === 'in_progress'
                          ? 'bg-purple-950/60 text-purple-400 border border-purple-800/40 animate-pulse'
                          : 'bg-dark-800 text-slate-400 border border-border-subtle'
                      }`}
                    >
                      {a.status.replace('_', ' ')}
                    </span>
                    <ArrowRight size={15} className="text-slate-500" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live Activity Stream */}
        <div className="bg-dark-900 border border-border-subtle rounded-xl p-6 space-y-4">
          <div>
            <h3 className="text-base font-semibold text-white">System Activity</h3>
            <p className="text-xs text-slate-400">Recent automation & publishing events</p>
          </div>

          <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
            {activities.length === 0 ? (
              <p className="text-xs text-slate-500 italic py-6 text-center">No activity recorded yet.</p>
            ) : (
              activities.slice(0, 8).map((act) => (
                <div key={act.id} className="p-2.5 rounded-lg bg-dark-850/80 border border-border-subtle space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-dark-800 text-slate-300 font-semibold uppercase">
                      {act.event_type}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-snug">{act.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const CheckCircleIcon: React.FC<{ size?: number; className?: string }> = ({ size = 18, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);

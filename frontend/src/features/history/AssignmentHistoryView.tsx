import React, { useState } from 'react';
import { Search, Filter, ArrowRight, FileCode, CheckCircle2, Clock, RotateCcw } from 'lucide-react';
import { Assignment } from '../../lib/types';

interface AssignmentHistoryViewProps {
  assignments: Assignment[];
  onSelectAssignment: (id: string) => void;
  onNewAssignment: () => void;
}

export const AssignmentHistoryView: React.FC<AssignmentHistoryViewProps> = ({
  assignments,
  onSelectAssignment,
  onNewAssignment,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [languageFilter, setLanguageFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const filtered = assignments.filter((a) => {
    const matchesSearch =
      a.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (a.week_module && a.week_module.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesLang = languageFilter === 'all' || a.language.toLowerCase() === languageFilter.toLowerCase();
    const matchesStatus = statusFilter === 'all' || a.status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesLang && matchesStatus;
  });

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 overflow-y-auto h-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Assignment History</h2>
          <p className="text-sm text-slate-400">
            Browse and inspect previously generated and published assignment solutions
          </p>
        </div>

        <button
          onClick={onNewAssignment}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-accent-violet to-accent-cyan text-white text-xs font-semibold shadow-sm hover:opacity-95"
        >
          + New Assignment
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3.5 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search assignments by title or module..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-dark-900 border border-border-default rounded-xl text-xs text-slate-200 focus:outline-none focus:border-accent-violet"
          />
        </div>

        <select
          value={languageFilter}
          onChange={(e) => setLanguageFilter(e.target.value)}
          className="bg-dark-900 border border-border-default rounded-xl px-3 py-2 text-xs text-slate-300 font-mono focus:outline-none"
        >
          <option value="all">All Languages</option>
          <option value="cpp">C++</option>
          <option value="c">C</option>
          <option value="java">Java</option>
          <option value="python">Python</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-dark-900 border border-border-default rounded-xl px-3 py-2 text-xs text-slate-300 font-mono focus:outline-none"
        >
          <option value="all">All Statuses</option>
          <option value="published">Published</option>
          <option value="ready_to_publish">Ready to Publish</option>
          <option value="in_progress">In Progress</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Table / List */}
      <div className="bg-dark-900 border border-border-subtle rounded-2xl overflow-hidden shadow-xl">
        {filtered.length === 0 ? (
          <div className="py-16 text-center text-slate-500 text-xs italic">
            No assignments match your search filter.
          </div>
        ) : (
          <div className="divide-y divide-border-subtle">
            {filtered.map((a) => (
              <div
                key={a.id}
                onClick={() => onSelectAssignment(a.id)}
                className="p-5 flex items-center justify-between hover:bg-dark-850 cursor-pointer transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-sm text-slate-200">{a.title}</span>
                    {a.week_module && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-dark-800 text-slate-400 border border-border-subtle">
                        {a.week_module}
                      </span>
                    )}
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-dark-800 text-accent-cyan uppercase font-semibold">
                      {a.language}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span>{a.questions?.length || 0} question(s)</span>
                    <span>•</span>
                    <span>ID: <code className="font-mono text-[11px] text-slate-500">{a.id}</code></span>
                    <span>•</span>
                    <span>{new Date(a.created_at).toLocaleString()}</span>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span
                    className={`text-xs font-mono px-3 py-1 rounded-full uppercase font-medium ${
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
                  <ArrowRight size={16} className="text-slate-500" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

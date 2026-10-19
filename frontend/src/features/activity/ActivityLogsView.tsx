import React, { useState } from 'react';
import { Activity, RefreshCw, CheckCircle2, AlertTriangle, XCircle, Info, Filter } from 'lucide-react';
import { ActivityLog } from '../../lib/types';

interface ActivityLogsViewProps {
  activities: ActivityLog[];
  onRefresh: () => void;
}

export const ActivityLogsView: React.FC<ActivityLogsViewProps> = ({ activities, onRefresh }) => {
  const [filterType, setFilterType] = useState('all');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await onRefresh();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const filtered = activities.filter((act) => {
    if (filterType === 'all') return true;
    return act.severity === filterType;
  });

  const getSeverityIcon = (sev: string) => {
    switch (sev) {
      case 'success':
        return <CheckCircle2 size={15} className="text-emerald-400" />;
      case 'warning':
        return <AlertTriangle size={15} className="text-amber-400" />;
      case 'error':
        return <XCircle size={15} className="text-rose-400" />;
      default:
        return <Info size={15} className="text-accent-cyan" />;
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 overflow-y-auto h-full select-none">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">System Activity Logs</h2>
          <p className="text-sm text-slate-400">
            Real-time audit log of assignment intake, sandbox executions, repairs, and GitHub operations
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-dark-900 border border-border-default rounded-xl px-3 py-1.5 text-xs text-slate-300 font-mono focus:outline-none"
          >
            <option value="all">All Severities</option>
            <option value="success">Success</option>
            <option value="info">Info</option>
            <option value="warning">Warnings</option>
            <option value="error">Errors</option>
          </select>

          <button
            onClick={handleRefresh}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-dark-900 border border-border-default text-xs text-slate-300 hover:text-white hover:bg-dark-850 transition-colors"
          >
            <RefreshCw size={13} className={isRefreshing ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <div className="bg-dark-900 border border-border-subtle rounded-2xl overflow-hidden shadow-xl divide-y divide-border-subtle">
        {filtered.length === 0 ? (
          <div className="py-16 text-center text-slate-500 text-xs italic">
            No activity logs found.
          </div>
        ) : (
          filtered.map((log) => (
            <div key={log.id} className="p-4 flex items-start gap-4 hover:bg-dark-850 transition-colors">
              <div className="mt-0.5 shrink-0">{getSeverityIcon(log.severity)}</div>

              <div className="space-y-1 flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-dark-800 text-slate-200 border border-border-subtle uppercase">
                      {log.event_type}
                    </span>
                    {log.job_id && (
                      <span className="text-[11px] font-mono text-slate-500">
                        job: {log.job_id}
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] font-mono text-slate-500 shrink-0">
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>

                <p className="text-xs text-slate-300 font-sans leading-relaxed">{log.message}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

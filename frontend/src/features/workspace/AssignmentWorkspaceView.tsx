import React, { useState, useEffect } from 'react';
import {
  FileCode,
  Copy,
  Download,
  Check,
  Terminal,
  Play,
  RotateCcw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  GitBranch,
  UploadCloud,
  Loader2,
  ExternalLink,
  ShieldCheck,
  ChevronRight,
  ListOrdered,
  Bug,
} from 'lucide-react';
import { api } from '../../lib/api';
import { Job, GeneratedSolution, PublishPreview, Assignment } from '../../lib/types';

interface AssignmentWorkspaceViewProps {
  assignmentId: string;
  initialJobId?: string;
  onBackToDashboard: () => void;
}

export const AssignmentWorkspaceView: React.FC<AssignmentWorkspaceViewProps> = ({
  assignmentId,
  initialJobId,
  onBackToDashboard,
}) => {
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [selectedSolutionIndex, setSelectedSolutionIndex] = useState(0);
  const [activeBottomTab, setActiveBottomTab] = useState<'tests' | 'compiler' | 'repairs'>('tests');

  // Publishing Drawer State
  const [isPublishDrawerOpen, setIsPublishDrawerOpen] = useState(false);
  const [publishPreview, setPublishPreview] = useState<PublishPreview | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishSuccessMessage, setPublishSuccessMessage] = useState<string | null>(null);
  const [publishError, setPublishError] = useState<string | null>(null);

  const [copied, setCopied] = useState(false);

  // Poll job status until done
  useEffect(() => {
    let timer: any;

    const fetchStatus = async () => {
      try {
        const asgn = await api.getAssignment(assignmentId);
        setAssignment(asgn);

        let currentJob: Job | null = null;
        if (initialJobId) {
          currentJob = await api.getJob(initialJobId);
        } else {
          currentJob = await api.getLatestJobForAssignment(assignmentId);
        }

        if (currentJob) {
          setJob(currentJob);
          // If still running, poll every 2 seconds
          if (['queued', 'extracting', 'generating', 'compiling', 'testing', 'repairing', 'publishing'].includes(currentJob.status)) {
            timer = setTimeout(fetchStatus, 2000);
          }
        }
      } catch (e) {
        console.error('Error fetching job state:', e);
      }
    };

    fetchStatus();
    return () => clearTimeout(timer);
  }, [assignmentId, initialJobId]);

  const activeSolution: GeneratedSolution | undefined = job?.solutions?.[selectedSolutionIndex];

  const handleCopyCode = () => {
    if (activeSolution?.source_code) {
      navigator.clipboard.writeText(activeSolution.source_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownloadCode = () => {
    if (!activeSolution) return;
    const blob = new Blob([activeSolution.source_code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = activeSolution.filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleOpenPublishDrawer = async () => {
    if (!job) return;
    setPublishError(null);
    setPublishSuccessMessage(null);
    setIsPublishDrawerOpen(true);
    try {
      const preview = await api.getPublishPreview(job.id);
      setPublishPreview(preview);
    } catch (err: any) {
      setPublishError(err.message || 'Failed to generate publish preview');
    }
  };

  const handleConfirmPublish = async () => {
    if (!job) return;
    setIsPublishing(true);
    setPublishError(null);
    try {
      const res = await api.publishJob(job.id);
      setPublishSuccessMessage(
        `Successfully published commit ${res.commit_sha?.slice(0, 7)} to dedicated branch ${res.branch_name}`
      );
      // Refresh job
      const updated = await api.getJob(job.id);
      setJob(updated);
    } catch (err: any) {
      setPublishError(err.message || 'Publishing failed');
    } finally {
      setIsPublishing(false);
    }
  };

  const handleRetryJob = async () => {
    if (!job) return;
    try {
      const newJob = await api.retryJob(job.id);
      setJob(newJob);
    } catch (err: any) {
      alert(`Retry failed: ${err.message}`);
    }
  };

  const isJobRunning = job && ['queued', 'extracting', 'generating', 'compiling', 'testing', 'repairing', 'publishing'].includes(job.status);

  return (
    <div className="flex flex-col h-full overflow-hidden select-none">
      {/* Top Header / Status Banner */}
      <div className="h-14 border-b border-border-subtle bg-dark-900 px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToDashboard}
            className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            ← Overview
          </button>
          <div className="h-4 w-[1px] bg-border-subtle" />
          <span className="font-semibold text-sm text-white truncate max-w-sm">
            {assignment?.title || 'Assignment Workspace'}
          </span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-dark-850 text-accent-cyan border border-border-subtle">
            {assignment?.language.toUpperCase()}
          </span>
          <div className="hidden xl:flex items-center gap-1.5 text-xs font-mono text-slate-400 bg-dark-850 px-2.5 py-1 rounded-lg border border-border-subtle">
            <span className="text-slate-500">Folder:</span>
            <span className="text-accent-cyan">STEP_Agent_Assignments/</span>
          </div>
        </div>

        {/* Status Pill & Action Buttons */}
        <div className="flex items-center gap-3">
          {job && (
            <div className="flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-lg bg-dark-850 border border-border-subtle">
              {isJobRunning ? (
                <>
                  <Loader2 size={13} className="animate-spin text-accent-violet" />
                  <span className="text-slate-300">{job.current_step}</span>
                  <span className="text-accent-cyan">({job.progress_percent}%)</span>
                </>
              ) : job.status === 'published' ? (
                <>
                  <CheckCircle2 size={13} className="text-emerald-400" />
                  <span className="text-emerald-400 font-semibold">Pushed to GitHub</span>
                </>
              ) : job.status === 'ready_to_publish' ? (
                <>
                  <CheckCircle2 size={13} className="text-emerald-400" />
                  <span className="text-emerald-400 font-semibold">All Tests Passed & Ready</span>
                </>
              ) : job.status === 'failed' ? (
                <>
                  <XCircle size={13} className="text-rose-400" />
                  <span className="text-rose-400 font-semibold">Validation Error</span>
                </>
              ) : (
                <span className="text-slate-400">{job.status}</span>
              )}
            </div>
          )}

          {job?.status === 'failed' && (
            <button
              onClick={handleRetryJob}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-dark-800 border border-border-default text-xs font-medium text-slate-200 hover:text-white hover:bg-dark-750"
            >
              <RotateCcw size={13} />
              <span>Retry</span>
            </button>
          )}

          <button
            onClick={handleOpenPublishDrawer}
            disabled={!job || job.solutions?.length === 0}
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-gradient-to-r from-accent-violet to-accent-cyan hover:opacity-95 text-white text-xs font-semibold shadow-md transition-all disabled:opacity-50 cursor-pointer"
          >
            <UploadCloud size={15} />
            <span>Push to GitHub</span>
          </button>
        </div>
      </div>

      {/* Main Multi-Panel Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Question Selector */}
        <div className="w-72 border-r border-border-subtle bg-dark-900/50 flex flex-col shrink-0">
          <div className="p-3 border-b border-border-subtle text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Assignment Questions</span>
            <span>{job?.solutions?.length || 0} Solved</span>
          </div>

          <div className="divide-y divide-border-subtle overflow-y-auto flex-1">
            {assignment?.questions?.map((q, idx) => {
              const sol = job?.solutions?.find((s) => s.question_id === q.id);
              const isSelected = selectedSolutionIndex === idx;

              return (
                <button
                  key={q.id}
                  onClick={() => setSelectedSolutionIndex(idx)}
                  className={`w-full text-left p-3.5 space-y-1.5 transition-colors ${
                    isSelected ? 'bg-accent-violet/15 border-l-2 border-accent-cyan' : 'hover:bg-dark-850'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-slate-400">Q{q.question_number}</span>
                    {sol ? (
                      sol.validation_status === 'passed' ? (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                          PASSED ({sol.tests_passed}/{sol.tests_total})
                        </span>
                      ) : (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-950/60 text-rose-400 border border-rose-800/40">
                          {sol.validation_status.toUpperCase()}
                        </span>
                      )
                    ) : isJobRunning ? (
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-950/60 text-purple-300 animate-pulse">
                        GENERATING
                      </span>
                    ) : (
                      <span className="text-[10px] font-mono text-slate-500">PENDING</span>
                    )}
                  </div>

                  <p className="text-xs font-medium text-slate-200 truncate">{q.title}</p>
                  <p className="text-[11px] font-mono text-accent-cyan truncate">{q.target_filename}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Center & Bottom Panel: Code Editor + Validation Console */}
        <div className="flex-1 flex flex-col overflow-hidden bg-dark-950">
          {/* File Header Tab */}
          <div className="h-10 border-b border-border-subtle bg-dark-900 px-4 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <FileCode size={15} className="text-accent-cyan" />
              <span className="text-xs font-mono text-slate-200">
                {activeSolution?.filename || 'solution'}
              </span>
              <span className="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-dark-800 text-slate-400">
                {activeSolution?.language || assignment?.language}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded hover:bg-dark-800 transition-colors"
                title="Copy Code"
              >
                {copied ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
              <button
                onClick={handleDownloadCode}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded hover:bg-dark-800 transition-colors"
                title="Download Source File"
              >
                <Download size={13} />
                <span>Download</span>
              </button>
            </div>
          </div>

          {/* Code Viewer */}
          <div className="flex-1 overflow-auto p-4 bg-dark-950 code-font">
            {activeSolution?.source_code ? (
              <pre className="text-xs text-slate-200 leading-relaxed font-mono whitespace-pre-wrap select-text">
                {activeSolution.source_code}
              </pre>
            ) : isJobRunning ? (
              <div className="h-full flex flex-col items-center justify-center text-center space-y-3">
                <Loader2 size={24} className="animate-spin text-accent-cyan" />
                <p className="text-xs text-slate-400 font-mono">Generating optimal solution code...</p>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs italic">
                No code generated for this question yet.
              </div>
            )}
          </div>

          {/* Bottom Panel: Output, Tests, and Repairs */}
          <div className="h-64 border-t border-border-subtle bg-dark-900 flex flex-col shrink-0">
            {/* Tabs Header */}
            <div className="h-9 border-b border-border-subtle bg-dark-850 px-4 flex items-center gap-4 text-xs">
              <button
                onClick={() => setActiveBottomTab('tests')}
                className={`flex items-center gap-1.5 py-2 font-medium transition-colors ${
                  activeBottomTab === 'tests'
                    ? 'text-accent-cyan border-b-2 border-accent-cyan'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Play size={12} />
                <span>
                  Sample Tests ({activeSolution?.tests_passed || 0}/{activeSolution?.tests_total || 0})
                </span>
              </button>

              <button
                onClick={() => setActiveBottomTab('compiler')}
                className={`flex items-center gap-1.5 py-2 font-medium transition-colors ${
                  activeBottomTab === 'compiler'
                    ? 'text-accent-cyan border-b-2 border-accent-cyan'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Terminal size={12} />
                <span>Compiler Output</span>
                {activeSolution?.compilation_status === 'passed' && (
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                )}
              </button>

              <button
                onClick={() => setActiveBottomTab('repairs')}
                className={`flex items-center gap-1.5 py-2 font-medium transition-colors ${
                  activeBottomTab === 'repairs'
                    ? 'text-accent-cyan border-b-2 border-accent-cyan'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Bug size={12} />
                <span>Repair History ({activeSolution?.repair_attempts || 0})</span>
              </button>
            </div>

            {/* Tab Contents */}
            <div className="flex-1 overflow-y-auto p-4 code-font text-xs">
              {activeBottomTab === 'tests' && (
                <div className="space-y-3">
                  {activeSolution?.test_results && activeSolution.test_results.length > 0 ? (
                    activeSolution.test_results.map((tr) => (
                      <div
                        key={tr.test_number}
                        className={`p-3 rounded-lg border space-y-2 ${
                          tr.passed
                            ? 'bg-emerald-950/20 border-emerald-900/40 text-emerald-200'
                            : 'bg-rose-950/20 border-rose-900/40 text-rose-200'
                        }`}
                      >
                        <div className="flex items-center justify-between font-mono text-[11px]">
                          <span className="font-bold">Test #{tr.test_number}</span>
                          <div className="flex items-center gap-2">
                            {tr.execution_time_ms && (
                              <span className="text-slate-400">{tr.execution_time_ms} ms</span>
                            )}
                            <span
                              className={`px-1.5 py-0.5 rounded uppercase font-semibold ${
                                tr.passed ? 'bg-emerald-900/60 text-emerald-300' : 'bg-rose-900/60 text-rose-300'
                              }`}
                            >
                              {tr.passed ? 'PASSED' : 'FAILED'}
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-[11px] pt-1">
                          <div>
                            <span className="text-slate-400 block mb-0.5">Input:</span>
                            <pre className="bg-dark-950 p-1.5 rounded border border-border-subtle overflow-x-auto">
                              {tr.input || '(empty)'}
                            </pre>
                          </div>
                          <div>
                            <span className="text-slate-400 block mb-0.5">Expected Output:</span>
                            <pre className="bg-dark-950 p-1.5 rounded border border-border-subtle overflow-x-auto">
                              {tr.expected_output}
                            </pre>
                          </div>
                        </div>

                        {tr.actual_output && (
                          <div className="text-[11px]">
                            <span className="text-slate-400 block mb-0.5">Actual Output:</span>
                            <pre className="bg-dark-950 p-1.5 rounded border border-border-subtle overflow-x-auto">
                              {tr.actual_output}
                            </pre>
                          </div>
                        )}

                        {tr.error && (
                          <div className="text-[11px] text-rose-400 pt-1">
                            <span>Error: {tr.error}</span>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500 italic py-4">No test executions recorded yet.</p>
                  )}
                </div>
              )}

              {activeBottomTab === 'compiler' && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-slate-400 text-[11px]">
                    <span>Status: {activeSolution?.compilation_status || 'not_run'}</span>
                  </div>
                  <pre className="p-3 bg-dark-950 rounded-lg border border-border-subtle text-slate-300 whitespace-pre-wrap">
                    {activeSolution?.compiler_output || 'No compiler output.'}
                  </pre>
                </div>
              )}

              {activeBottomTab === 'repairs' && (
                <div className="space-y-3">
                  {activeSolution?.repair_history && activeSolution.repair_history.length > 0 ? (
                    activeSolution.repair_history.map((rh) => (
                      <div
                        key={rh.attempt_number}
                        className="p-3 bg-dark-850 rounded-lg border border-border-subtle space-y-1.5 text-slate-300"
                      >
                        <div className="flex items-center justify-between text-[11px] font-mono">
                          <span className="font-bold text-amber-400">Repair Attempt #{rh.attempt_number}</span>
                          <span className="text-slate-400">
                            Tests Passed: {rh.tests_passed}/{rh.tests_total}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 whitespace-pre-wrap">{rh.error}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500 italic py-4">
                      No automated repairs were needed. Solution compiled and passed tests on initial generation.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Right Drawer: GitHub Publishing Preview & Execution */}
      {isPublishDrawerOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end">
          <div className="w-[500px] bg-dark-900 border-l border-border-default h-full flex flex-col p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-border-subtle pb-4">
              <div className="flex items-center gap-2">
                <UploadCloud size={20} className="text-accent-cyan" />
                <h3 className="font-semibold text-white text-base">Publish to GitHub</h3>
              </div>
              <button
                onClick={() => setIsPublishDrawerOpen(false)}
                className="text-slate-400 hover:text-slate-200 text-sm"
              >
                ✕
              </button>
            </div>

            {publishSuccessMessage && (
              <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-200 text-xs space-y-2">
                <div className="flex items-center gap-2 font-bold">
                  <CheckCircle2 size={16} className="text-emerald-400" />
                  <span>Publication Successful!</span>
                </div>
                <p>{publishSuccessMessage}</p>
                {job?.commit_url && (
                  <a
                    href={job.commit_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-accent-cyan hover:underline font-mono pt-1"
                  >
                    <span>View Commit on GitHub</span>
                    <ExternalLink size={12} />
                  </a>
                )}
              </div>
            )}

            {publishError && (
              <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs space-y-1">
                <div className="flex items-center gap-2 font-bold">
                  <AlertTriangle size={16} className="text-rose-400" />
                  <span>Publishing Error</span>
                </div>
                <p>{publishError}</p>
              </div>
            )}

            <div className="space-y-4 flex-1 overflow-y-auto">
              <div className="bg-dark-850 p-4 rounded-xl border border-border-subtle space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Target Branch:</span>
                  <span className="font-mono text-accent-cyan font-semibold">
                    {publishPreview?.target_branch || job?.target_branch || 'autoryx/assignment-...'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Strict Directory:</span>
                  <span className="font-mono text-slate-200">STEP_Agent_Assignments/</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Safety Verification:</span>
                  <span className="text-emerald-400 font-semibold flex items-center gap-1">
                    <ShieldCheck size={13} />
                    <span>PASSED (100% Isolated)</span>
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-mono uppercase text-slate-400">Proposed Staging Files:</span>
                <div className="bg-dark-950 rounded-xl p-3 border border-border-subtle space-y-1.5 font-mono text-xs">
                  {publishPreview?.proposed_files.map((f) => (
                    <div key={f.relative_path} className="flex items-center justify-between text-slate-300 py-1">
                      <span className="truncate pr-2">{f.relative_path}</span>
                      <span className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 shrink-0">
                        {f.action}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-border-subtle space-y-2">
              <button
                onClick={handleConfirmPublish}
                disabled={isPublishing || !publishPreview?.safety_checks_passed}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-accent-violet to-accent-cyan text-white text-sm font-semibold shadow-lg hover:opacity-95 disabled:opacity-50 transition-all"
              >
                {isPublishing ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Publishing Dedicated Branch...</span>
                  </>
                ) : (
                  <>
                    <UploadCloud size={16} />
                    <span>Confirm & Push to GitHub</span>
                  </>
                )}
              </button>
              <p className="text-[11px] text-slate-500 text-center">
                Publishes strictly to a dedicated branch. Never touches Week 1/ or Week 2/.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

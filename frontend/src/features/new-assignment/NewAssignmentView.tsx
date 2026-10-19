import React, { useState } from 'react';
import {
  Upload,
  FileText,
  FileCode,
  ArrowRight,
  Sparkles,
  Check,
  AlertCircle,
  Plus,
  Trash2,
  Edit2,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { api } from '../../lib/api';
import { Assignment, Question } from '../../lib/types';

interface NewAssignmentViewProps {
  onAssignmentCreated: (assignmentId: string) => void;
  onJobStarted: (jobId: string, assignmentId: string) => void;
}

export const NewAssignmentView: React.FC<NewAssignmentViewProps> = ({
  onAssignmentCreated,
  onJobStarted,
}) => {
  const [tab, setTab] = useState<'upload' | 'paste'>('upload');
  const [title, setTitle] = useState('');
  const [weekModule, setWeekModule] = useState('Week 3');
  const [language, setLanguage] = useState('cpp');
  const [pastedText, setPastedText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Review stage
  const [createdAssignment, setCreatedAssignment] = useState<Assignment | null>(null);
  const [reviewQuestions, setReviewQuestions] = useState<Question[]>([]);
  const [isStartingJob, setIsStartingJob] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setSelectedFile(f);
      if (!title) {
        setTitle(f.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const f = e.dataTransfer.files[0];
      setSelectedFile(f);
      if (!title) {
        setTitle(f.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleProcessIntake = async () => {
    setError(null);
    setIsLoading(true);

    try {
      let assignment: Assignment;
      if (tab === 'upload') {
        if (!selectedFile) {
          setError('Please select or drop a PDF, TXT, or image assignment file.');
          setIsLoading(false);
          return;
        }
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('title', title || selectedFile.name);
        if (weekModule) formData.append('week_module', weekModule);
        formData.append('language', language);

        assignment = await api.uploadAssignment(formData);
      } else {
        if (!pastedText.trim()) {
          setError('Please paste the assignment questions and constraints.');
          setIsLoading(false);
          return;
        }
        assignment = await api.createFromText({
          title: title || 'Pasted Assignment',
          week_module: weekModule || undefined,
          language,
          text: pastedText,
        });
      }

      setCreatedAssignment(assignment);
      setReviewQuestions(assignment.questions || []);
      onAssignmentCreated(assignment.id);
    } catch (err: any) {
      setError(err.message || 'Failed to process assignment');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAutoProcess = async () => {
    setError(null);
    setIsLoading(true);

    try {
      let assignment: Assignment;
      if (tab === 'upload') {
        if (!selectedFile) {
          setError('Please select or drop an assignment PDF file first.');
          setIsLoading(false);
          return;
        }
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('title', title || selectedFile.name.replace(/\.[^/.]+$/, ''));
        if (weekModule) formData.append('week_module', weekModule);
        formData.append('language', language);

        assignment = await api.uploadAssignment(formData);
      } else {
        if (!pastedText.trim()) {
          setError('Please paste the assignment questions.');
          setIsLoading(false);
          return;
        }
        assignment = await api.createFromText({
          title: title || 'Pasted Assignment',
          week_module: weekModule || undefined,
          language,
          text: pastedText,
        });
      }

      onAssignmentCreated(assignment.id);

      // Immediately launch the background automation job!
      const job = await api.createJob(assignment.id);
      onJobStarted(job.id, assignment.id);
    } catch (err: any) {
      setError(err.message || 'Failed to auto-process assignment');
      setIsLoading(false);
    }
  };

  const handleQuestionChange = (index: number, field: keyof Question, value: any) => {
    const updated = [...reviewQuestions];
    updated[index] = { ...updated[index], [field]: value };
    setReviewQuestions(updated);
  };

  const handleSaveQuestion = async (q: Question) => {
    if (!createdAssignment) return;
    try {
      await api.updateQuestion(createdAssignment.id, q.id, {
        title: q.title,
        description: q.description,
        constraints: q.constraints,
        target_filename: q.target_filename,
        sample_inputs: q.sample_inputs,
        sample_outputs: q.sample_outputs,
        is_approved: q.is_approved,
      });
    } catch (e: any) {
      setError(`Failed to save question: ${e.message}`);
    }
  };

  const handleStartAutomation = async () => {
    if (!createdAssignment) return;
    setIsStartingJob(true);
    setError(null);

    try {
      // Sync all questions before starting
      for (const q of reviewQuestions) {
        await api.updateQuestion(createdAssignment.id, q.id, {
          title: q.title,
          description: q.description,
          constraints: q.constraints,
          target_filename: q.target_filename,
          sample_inputs: q.sample_inputs,
          sample_outputs: q.sample_outputs,
          is_approved: q.is_approved,
        });
      }

      // Create persistent job
      const job = await api.createJob(createdAssignment.id);
      onJobStarted(job.id, createdAssignment.id);
    } catch (err: any) {
      setError(err.message || 'Failed to start automation job');
      setIsStartingJob(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 overflow-y-auto h-full">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white">New Assignment Intake</h2>
        <p className="text-sm text-slate-400">
          Upload assignment documents, extract questions, verify filenames, and run AI generation.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/50 border border-rose-800 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle size={18} className="shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {!createdAssignment ? (
        /* STEP 1: Intake Form */
        <div className="bg-dark-900 border border-border-subtle rounded-2xl p-6 space-y-6 shadow-xl">
          {/* Metadata Controls */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-mono uppercase text-slate-300">Assignment Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Week 3 Algorithms"
                className="w-full bg-dark-850 border border-border-default rounded-lg px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-accent-violet"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono uppercase text-slate-300">Week / Module (Folder Tag)</label>
              <input
                type="text"
                value={weekModule}
                onChange={(e) => setWeekModule(e.target.value)}
                placeholder="e.g. Week 3"
                className="w-full bg-dark-850 border border-border-default rounded-lg px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-accent-violet"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-mono uppercase text-slate-300">Target Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full bg-dark-850 border border-border-default rounded-lg px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-accent-violet font-mono"
              >
                <option value="cpp">C++ (g++ 14.2 / C++17)</option>
                <option value="c">C (gcc 14.2 / C11)</option>
                <option value="java">Java (JDK 25 / javac)</option>
                <option value="python">Python (Python 3.13)</option>
              </select>
            </div>
          </div>

          {/* Intake Tabs */}
          <div className="flex items-center gap-2 border-b border-border-subtle pb-3">
            <button
              onClick={() => setTab('upload')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                tab === 'upload'
                  ? 'bg-accent-violet/20 text-accent-cyan border border-accent-violet/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Upload size={14} />
              <span>Document Upload (PDF / TXT / Images)</span>
            </button>
            <button
              onClick={() => setTab('paste')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                tab === 'paste'
                  ? 'bg-accent-violet/20 text-accent-cyan border border-accent-violet/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileText size={14} />
              <span>Paste Assignment Text</span>
            </button>
          </div>

          {/* Upload Area */}
          {tab === 'upload' ? (
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="border-2 border-dashed border-border-default hover:border-accent-violet/60 rounded-xl p-10 text-center space-y-4 bg-dark-850/50 transition-colors cursor-pointer"
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <input
                id="file-upload"
                type="file"
                accept=".pdf,.txt,.md,.png,.jpg,.jpeg"
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="w-12 h-12 rounded-full bg-dark-800 border border-border-subtle mx-auto flex items-center justify-center text-accent-cyan">
                <Upload size={22} />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-200">
                  {selectedFile ? (
                    <span className="text-accent-cyan font-mono">{selectedFile.name}</span>
                  ) : (
                    'Click to select or drag and drop assignment document'
                  )}
                </p>
                <p className="text-xs text-slate-500">Supports PDF, scanned images, and plain text up to 25 MB</p>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <label className="text-xs font-mono uppercase text-slate-400">Pasted Assignment Text</label>
              <textarea
                rows={10}
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Paste the assignment description, Question 1, Question 2, constraints, sample inputs and outputs here..."
                className="w-full bg-dark-850 border border-border-default rounded-xl p-4 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet leading-relaxed"
              />
            </div>
          )}

          {/* Submit Action */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-3 border-t border-border-subtle">
            <div className="text-xs text-slate-400 font-mono">
              Workflow: <span className="text-slate-200">Upload → AI Generate → Compile → Sandbox Test → Push to GitHub</span>
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <button
                type="button"
                onClick={handleProcessIntake}
                disabled={isLoading}
                className="px-4 py-2.5 rounded-xl bg-dark-800 border border-border-default text-slate-300 hover:text-white text-xs font-semibold hover:bg-dark-750 transition-all disabled:opacity-50"
              >
                Review Questions First
              </button>

              <button
                type="button"
                onClick={handleAutoProcess}
                disabled={isLoading}
                className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-accent-violet to-accent-cyan text-white text-sm font-semibold shadow-lg hover:opacity-95 disabled:opacity-50 transition-all flex-1 sm:flex-none cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Processing Assignment...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} className="text-yellow-300" />
                    <span>Auto-Process Assignment</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* STEP 2: Question Review & Approval Screen */
        <div className="space-y-6">
          <div className="bg-dark-900 border border-border-subtle rounded-2xl p-5 flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white">{createdAssignment.title}</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-dark-800 text-accent-cyan border border-border-subtle">
                  {createdAssignment.language.toUpperCase()}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  ({reviewQuestions.length} question(s) identified)
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Review extracted statements, target filenames, and sample test cases. You can edit any field before generation.
              </p>
            </div>

            <button
              onClick={handleStartAutomation}
              disabled={isStartingJob || reviewQuestions.filter((q) => q.is_approved).length === 0}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 text-white text-sm font-semibold shadow-lg shadow-emerald-500/20 hover:opacity-95 disabled:opacity-50 transition-all shrink-0"
            >
              {isStartingJob ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Enqueuing Cloud Job...</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Approve & Start Automation</span>
                </>
              )}
            </button>
          </div>

          {/* Questions List */}
          <div className="space-y-4">
            {reviewQuestions.map((q, idx) => (
              <div
                key={q.id || idx}
                className={`bg-dark-900 border rounded-2xl p-6 space-y-4 transition-all ${
                  q.is_approved ? 'border-border-default' : 'border-border-subtle opacity-60'
                }`}
              >
                <div className="flex items-center justify-between pb-3 border-b border-border-subtle">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={q.is_approved}
                      onChange={(e) => handleQuestionChange(idx, 'is_approved', e.target.checked)}
                      className="w-4 h-4 rounded text-accent-violet focus:ring-0 bg-dark-800 border-border-default cursor-pointer"
                    />
                    <span className="text-xs font-mono font-bold text-accent-cyan uppercase">
                      Question {q.question_number}
                    </span>
                    <input
                      type="text"
                      value={q.title}
                      onChange={(e) => handleQuestionChange(idx, 'title', e.target.value)}
                      className="bg-dark-850 border border-border-subtle rounded px-2.5 py-1 text-sm text-slate-200 font-medium focus:outline-none focus:border-accent-violet w-72"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-400">Target File:</span>
                    <input
                      type="text"
                      value={q.target_filename}
                      onChange={(e) => handleQuestionChange(idx, 'target_filename', e.target.value)}
                      className="bg-dark-850 border border-border-subtle rounded px-2.5 py-1 text-xs text-accent-cyan font-mono focus:outline-none focus:border-accent-violet w-40"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-mono uppercase text-slate-400">Problem Statement</label>
                  <textarea
                    rows={4}
                    value={q.description}
                    onChange={(e) => handleQuestionChange(idx, 'description', e.target.value)}
                    className="w-full bg-dark-850 border border-border-subtle rounded-xl p-3 text-xs text-slate-200 font-mono leading-relaxed focus:outline-none focus:border-accent-violet"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-mono uppercase text-slate-400">Sample Input</label>
                    <textarea
                      rows={2}
                      value={q.sample_inputs?.join('\n---\n') || ''}
                      onChange={(e) =>
                        handleQuestionChange(idx, 'sample_inputs', e.target.value.split('\n---\n'))
                      }
                      placeholder="Input tokens..."
                      className="w-full bg-dark-850 border border-border-subtle rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-accent-violet"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-mono uppercase text-slate-400">Sample Expected Output</label>
                    <textarea
                      rows={2}
                      value={q.sample_outputs?.join('\n---\n') || ''}
                      onChange={(e) =>
                        handleQuestionChange(idx, 'sample_outputs', e.target.value.split('\n---\n'))
                      }
                      placeholder="Expected output..."
                      className="w-full bg-dark-850 border border-border-subtle rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:outline-none focus:border-accent-violet"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center pt-4">
            <button
              onClick={() => setCreatedAssignment(null)}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              ← Back to Upload
            </button>

            <button
              onClick={handleStartAutomation}
              disabled={isStartingJob}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 text-white text-sm font-semibold shadow-lg hover:opacity-95 disabled:opacity-50 transition-all"
            >
              {isStartingJob ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
              <span>Approve All & Run Automation</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import {
  Save,
  CheckCircle2,
  AlertTriangle,
  Key,
  FolderGit2,
  Cpu,
  Shield,
  Loader2,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import { api } from '../../lib/api';
import { Settings } from '../../lib/types';

export const SettingsView: React.FC = () => {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form Fields
  const [githubOwner, setGithubOwner] = useState('');
  const [githubRepo, setGithubRepo] = useState('');
  const [githubDefaultBranch, setGithubDefaultBranch] = useState('main');
  const [githubToken, setGithubToken] = useState('');

  const [aiProvider, setAiProvider] = useState<'gemini' | 'openai' | 'mock'>('gemini');
  const [geminiKey, setGeminiKey] = useState('');
  const [geminiModel, setGeminiModel] = useState('gemini-2.5-flash');
  const [openaiKey, setOpenaiKey] = useState('');
  const [openaiModel, setOpenaiModel] = useState('gpt-4o');

  const [maxRepairs, setMaxRepairs] = useState(2);
  const [autoPublish, setAutoPublish] = useState(false);

  // Test Connection States
  const [testingGitHub, setTestingGitHub] = useState(false);
  const [gitHubTestResult, setGitHubTestResult] = useState<string | null>(null);

  const [testingAI, setTestingAI] = useState(false);
  const [aiTestResult, setAiTestResult] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setIsLoading(true);
    try {
      const data = await api.getSettings();
      setSettings(data);
      setGithubOwner(data.github_owner);
      setGithubRepo(data.github_repo);
      setGithubDefaultBranch(data.github_default_branch);
      setAiProvider(data.ai_provider);
      setGeminiModel(data.gemini_model);
      setOpenaiModel(data.openai_model);
      setMaxRepairs(data.max_repair_attempts);
      setAutoPublish(data.auto_publish_branch);
    } catch (e: any) {
      setError(e.message || 'Failed to fetch settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSaveSuccess(false);
    try {
      const updated = await api.updateSettings({
        github_owner: githubOwner,
        github_repo: githubRepo,
        github_default_branch: githubDefaultBranch,
        github_token: githubToken ? githubToken : undefined,
        ai_provider: aiProvider,
        gemini_key: geminiKey ? geminiKey : undefined,
        gemini_model: geminiModel,
        openai_key: openaiKey ? openaiKey : undefined,
        openai_model: openaiModel,
        max_repair_attempts: maxRepairs,
        auto_publish_branch: autoPublish,
      });
      setSettings(updated);
      setSaveSuccess(true);
      setGithubToken('');
      setGeminiKey('');
      setOpenaiKey('');
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (e: any) {
      setError(e.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestGitHub = async () => {
    setTestingGitHub(true);
    setGitHubTestResult(null);
    try {
      const res = await api.testGitHub();
      setGitHubTestResult(res.message);
    } catch (e: any) {
      setGitHubTestResult(`Error: ${e.message}`);
    } finally {
      setTestingGitHub(false);
    }
  };

  const handleTestAI = async () => {
    setTestingAI(true);
    setAiTestResult(null);
    try {
      const res = await api.testAI();
      if (res.success) {
        setAiTestResult(`Success! Model responded using ${res.provider}.`);
      } else {
        setAiTestResult(`Failed: ${res.error}`);
      }
    } catch (e: any) {
      setAiTestResult(`Error: ${e.message}`);
    } finally {
      setTestingAI(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400 text-xs">
        <Loader2 size={20} className="animate-spin text-accent-cyan mr-2" />
        <span>Loading Autoryx Configuration...</span>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 overflow-y-auto h-full select-none">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">System Settings & Configuration</h2>
          <p className="text-sm text-slate-400">
            Configure target GitHub repository access, AI generation model providers, and sandbox limits
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-accent-violet to-accent-cyan text-white text-xs font-semibold shadow-md hover:opacity-95 disabled:opacity-50 transition-all"
        >
          {isSaving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
          <span>{isSaving ? 'Saving...' : 'Save Configuration'}</span>
        </button>
      </div>

      {saveSuccess && (
        <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-200 text-xs flex items-center gap-2 font-medium">
          <CheckCircle2 size={16} className="text-emerald-400" />
          <span>Configuration saved successfully!</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle size={16} className="text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* SECTION 1: Target GitHub Repository */}
      <div className="bg-dark-900 border border-border-default rounded-2xl p-6 space-y-5 shadow-xl">
        <div className="flex items-center justify-between border-b border-border-subtle pb-3">
          <div className="flex items-center gap-2.5">
            <FolderGit2 size={18} className="text-accent-cyan" />
            <h3 className="text-sm font-semibold text-white">GitHub Publishing Destination</h3>
          </div>
          <button
            onClick={handleTestGitHub}
            disabled={testingGitHub}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-dark-800 hover:bg-dark-750 text-slate-300 border border-border-subtle text-xs transition-colors"
          >
            {testingGitHub ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
            <span>Test Connection</span>
          </button>
        </div>

        {gitHubTestResult && (
          <div className="p-3 rounded-lg bg-dark-850 border border-border-subtle text-xs font-mono text-slate-300">
            {gitHubTestResult}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-slate-300">Repository Owner</label>
            <input
              type="text"
              value={githubOwner}
              onChange={(e) => setGithubOwner(e.target.value)}
              className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-slate-300">Repository Name</label>
            <input
              type="text"
              value={githubRepo}
              onChange={(e) => setGithubRepo(e.target.value)}
              className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-slate-300">Default Base Branch</label>
            <input
              type="text"
              value={githubDefaultBranch}
              onChange={(e) => setGithubDefaultBranch(e.target.value)}
              className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-mono uppercase text-slate-300">Personal Access Token (PAT)</label>
              {settings?.has_github_token && (
                <span className="text-[10px] font-mono text-emerald-400">
                  Configured: {settings.github_token_masked}
                </span>
              )}
            </div>
            <input
              type="password"
              placeholder={settings?.has_github_token ? 'Enter new token to replace existing' : 'ghp_...'}
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
            />
            <p className="text-[11px] text-slate-500">
              Fine-grained PAT with Repository Contents: Read & Write permissions. Never exposed to frontend.
            </p>
          </div>
        </div>
      </div>

      {/* SECTION 2: AI Provider & Models */}
      <div className="bg-dark-900 border border-border-default rounded-2xl p-6 space-y-5 shadow-xl">
        <div className="flex items-center justify-between border-b border-border-subtle pb-3">
          <div className="flex items-center gap-2.5">
            <Cpu size={18} className="text-accent-violet" />
            <h3 className="text-sm font-semibold text-white">AI Model & Generation Provider</h3>
          </div>
          <button
            onClick={handleTestAI}
            disabled={testingAI}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-dark-800 hover:bg-dark-750 text-slate-300 border border-border-subtle text-xs transition-colors"
          >
            {testingAI ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
            <span>Test Generation</span>
          </button>
        </div>

        {aiTestResult && (
          <div className="p-3 rounded-lg bg-dark-850 border border-border-subtle text-xs font-mono text-slate-300">
            {aiTestResult}
          </div>
        )}

        <div className="space-y-1.5">
          <label className="text-xs font-mono uppercase text-slate-300">Active AI Provider</label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'gemini', label: 'Google Gemini', sub: 'Gemini 2.5 Flash / Pro' },
              { id: 'openai', label: 'OpenAI', sub: 'GPT-4o / GPT-4o-mini' },
              { id: 'mock', label: 'Offline Engine', sub: 'Zero-cost local testing' },
            ].map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => setAiProvider(p.id as any)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  aiProvider === p.id
                    ? 'bg-accent-violet/15 border-accent-violet text-white shadow-sm'
                    : 'bg-dark-850 border-border-subtle text-slate-400 hover:bg-dark-800'
                }`}
              >
                <div className="text-xs font-semibold">{p.label}</div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">{p.sub}</div>
              </button>
            ))}
          </div>
        </div>

        {aiProvider === 'gemini' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-mono uppercase text-slate-300">Gemini Model</label>
              <input
                type="text"
                value={geminiModel}
                onChange={(e) => setGeminiModel(e.target.value)}
                className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
              />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-mono uppercase text-slate-300">Gemini API Key</label>
                {settings?.has_gemini_key && (
                  <span className="text-[10px] font-mono text-emerald-400">
                    Saved: {settings.gemini_key_masked}
                  </span>
                )}
              </div>
              <input
                type="password"
                placeholder={settings?.has_gemini_key ? 'Enter new key to replace existing' : 'AIza...'}
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
              />
            </div>
          </div>
        )}

        {aiProvider === 'openai' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-mono uppercase text-slate-300">OpenAI Model</label>
              <input
                type="text"
                value={openaiModel}
                onChange={(e) => setOpenaiModel(e.target.value)}
                className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
              />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-mono uppercase text-slate-300">OpenAI API Key</label>
                {settings?.has_openai_key && (
                  <span className="text-[10px] font-mono text-emerald-400">
                    Saved: {settings.openai_key_masked}
                  </span>
                )}
              </div>
              <input
                type="password"
                placeholder={settings?.has_openai_key ? 'Enter new key to replace' : 'sk-...'}
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
              />
            </div>
          </div>
        )}
      </div>

      {/* SECTION 3: Validation, Repair & Sandbox */}
      <div className="bg-dark-900 border border-border-default rounded-2xl p-6 space-y-5 shadow-xl">
        <div className="flex items-center gap-2.5 border-b border-border-subtle pb-3">
          <Shield size={18} className="text-emerald-400" />
          <h3 className="text-sm font-semibold text-white">Validation & Automatic Repair</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-slate-300">
              Maximum Repair Attempts (Default: 2)
            </label>
            <input
              type="number"
              min={0}
              max={5}
              value={maxRepairs}
              onChange={(e) => setMaxRepairs(parseInt(e.target.value) || 0)}
              className="w-full bg-dark-850 border border-border-default rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-violet"
            />
            <p className="text-[11px] text-slate-500">
              Bounds automated code correction retries when compiler or test errors occur.
            </p>
          </div>

          <div className="space-y-3 pt-2">
            <label className="text-xs font-mono uppercase text-slate-300 block">Publishing Safety</label>
            <div className="flex items-center gap-3">
              <input
                id="auto-pub-toggle"
                type="checkbox"
                checked={autoPublish}
                onChange={(e) => setAutoPublish(e.target.checked)}
                className="w-4 h-4 rounded text-accent-violet focus:ring-0 bg-dark-800 border-border-default cursor-pointer"
              />
              <label htmlFor="auto-pub-toggle" className="text-xs text-slate-300 cursor-pointer">
                Automatically push to dedicated branch upon validation pass
              </label>
            </div>
            <p className="text-[11px] text-slate-500">
              When disabled, jobs pause at "Ready to Publish" allowing manual code inspection before pushing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

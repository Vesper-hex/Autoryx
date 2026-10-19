import React, { useState, useEffect } from 'react';
import {
  Folder,
  FileText,
  FileCode,
  GitBranch,
  ExternalLink,
  ChevronRight,
  FolderGit2,
  ShieldCheck,
  Eye,
  Loader2,
} from 'lucide-react';
import { api } from '../../lib/api';
import { RepositoryItem } from '../../lib/types';

interface RepositoryExplorerViewProps {
  repoOwner: string;
  repoName: string;
  defaultBranch: string;
}

export const RepositoryExplorerView: React.FC<RepositoryExplorerViewProps> = ({
  repoOwner,
  repoName,
  defaultBranch,
}) => {
  const [currentPath, setCurrentPath] = useState('');
  const [items, setItems] = useState<RepositoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [loadingFile, setLoadingFile] = useState(false);

  const fetchDirectory = async (path: string) => {
    setIsLoading(true);
    setError(null);
    setSelectedFile(null);
    setFileContent(null);
    try {
      const data = await api.getRepoContents(path);
      // Sort directories first, then files
      const sorted = (Array.isArray(data) ? data : []).sort((a, b) => {
        if (a.type === 'dir' && b.type !== 'dir') return -1;
        if (a.type !== 'dir' && b.type === 'dir') return 1;
        return a.name.localeCompare(b.name);
      });
      setItems(sorted);
      setCurrentPath(path);
    } catch (e: any) {
      setError(e.message || 'Failed to fetch repository contents');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDirectory('');
  }, []);

  const handleItemClick = (item: RepositoryItem) => {
    if (item.type === 'dir') {
      fetchDirectory(item.path);
    } else {
      loadFile(item.path);
    }
  };

  const loadFile = async (filePath: string) => {
    setSelectedFile(filePath);
    setLoadingFile(true);
    try {
      const res = await api.getRepoFile(filePath, defaultBranch);
      setFileContent(res.content);
    } catch (e: any) {
      setFileContent(`Error loading file: ${e.message}`);
    } finally {
      setLoadingFile(false);
    }
  };

  const handleBreadcrumbClick = (idx: number) => {
    if (idx === -1) {
      fetchDirectory('');
      return;
    }
    const parts = currentPath.split('/');
    const target = parts.slice(0, idx + 1).join('/');
    fetchDirectory(target);
  };

  const breadcrumbParts = currentPath ? currentPath.split('/') : [];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 overflow-y-auto h-full select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white">GitHub Repository Explorer</h2>
            <a
              href={`https://github.com/${repoOwner}/${repoName}`}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-accent-cyan hover:underline flex items-center gap-1 font-mono"
            >
              <span>{repoOwner}/{repoName}</span>
              <ExternalLink size={12} />
            </a>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time file tree inspects remote branches and confirms isolated output structure.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-dark-900 border border-border-default text-xs font-mono text-slate-300">
            <GitBranch size={13} className="text-accent-cyan" />
            <span>branch: {defaultBranch}</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-xs text-emerald-300">
            <ShieldCheck size={13} />
            <span>Week 1/ & Week 2/ Protected</span>
          </div>
        </div>
      </div>

      {/* GitHub Explorer Container */}
      <div className="bg-dark-900 border border-border-default rounded-2xl overflow-hidden shadow-2xl flex flex-col min-h-[500px]">
        {/* GitHub Breadcrumbs Bar */}
        <div className="h-12 border-b border-border-subtle bg-dark-850 px-5 flex items-center justify-between">
          <div className="flex items-center gap-1 text-xs font-mono text-slate-300 overflow-x-auto">
            <button
              onClick={() => handleBreadcrumbClick(-1)}
              className="text-accent-cyan hover:underline font-bold"
            >
              {repoName}
            </button>
            {breadcrumbParts.map((part, idx) => (
              <React.Fragment key={idx}>
                <span className="text-slate-500">/</span>
                <button
                  onClick={() => handleBreadcrumbClick(idx)}
                  className="hover:underline text-slate-200"
                >
                  {part}
                </button>
              </React.Fragment>
            ))}
          </div>

          <div className="text-[11px] font-mono text-slate-500">
            {items.length} item(s)
          </div>
        </div>

        {/* Dual Panel: File Tree & File Content Viewer */}
        <div className="flex-1 flex overflow-hidden">
          {/* File Tree List */}
          <div className="w-1/2 border-r border-border-subtle overflow-y-auto divide-y divide-border-subtle">
            {isLoading ? (
              <div className="py-16 text-center text-slate-400 text-xs flex flex-col items-center gap-2">
                <Loader2 size={20} className="animate-spin text-accent-cyan" />
                <span>Fetching repository tree...</span>
              </div>
            ) : items.length === 0 ? (
              <div className="py-16 text-center text-slate-500 text-xs italic">
                Directory is empty.
              </div>
            ) : (
              items.map((item) => {
                const isDedicatedFolder = item.name === 'STEP_Agent_Assignments';
                const isWeekFolder = item.name === 'Week 1' || item.name === 'Week 2';
                const isSelected = selectedFile === item.path;

                return (
                  <button
                    key={item.path}
                    onClick={() => handleItemClick(item)}
                    className={`w-full flex items-center justify-between px-4 py-3 text-left transition-colors ${
                      isSelected
                        ? 'bg-accent-violet/20 border-l-2 border-accent-cyan'
                        : 'hover:bg-dark-850'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 overflow-hidden">
                      {item.type === 'dir' ? (
                        <Folder
                          size={16}
                          className={
                            isDedicatedFolder
                              ? 'text-accent-cyan fill-accent-cyan/20'
                              : isWeekFolder
                              ? 'text-indigo-400 fill-indigo-400/20'
                              : 'text-amber-400'
                          }
                        />
                      ) : (
                        <FileCode size={16} className="text-slate-400 shrink-0" />
                      )}

                      <span className="text-xs font-mono text-slate-200 truncate">{item.name}</span>

                      {isDedicatedFolder && (
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-accent-violet/20 text-accent-cyan font-semibold shrink-0">
                          AUTORYX OUTPUT
                        </span>
                      )}
                      {isWeekFolder && (
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-dark-800 text-slate-400 shrink-0">
                          READ-ONLY
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {item.size && (
                        <span className="text-[10px] font-mono text-slate-500">
                          {Math.round(item.size / 1024)} KB
                        </span>
                      )}
                      <ChevronRight size={13} className="text-slate-600" />
                    </div>
                  </button>
                );
              })
            )}
          </div>

          {/* File Content Preview */}
          <div className="w-1/2 flex flex-col overflow-hidden bg-dark-950">
            {selectedFile ? (
              <>
                <div className="h-10 border-b border-border-subtle bg-dark-900 px-4 flex items-center justify-between shrink-0">
                  <span className="text-xs font-mono text-slate-300 truncate">{selectedFile}</span>
                  <Eye size={14} className="text-slate-500" />
                </div>
                <div className="flex-1 overflow-auto p-4 code-font text-xs">
                  {loadingFile ? (
                    <div className="py-12 text-center text-slate-500 flex flex-col items-center gap-2">
                      <Loader2 size={16} className="animate-spin text-accent-cyan" />
                      <span>Loading file content...</span>
                    </div>
                  ) : (
                    <pre className="text-slate-200 whitespace-pre-wrap select-text leading-relaxed">
                      {fileContent}
                    </pre>
                  )}
                </div>
              </>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500 space-y-2">
                <FileText size={32} className="text-slate-600" />
                <p className="text-xs">Click a file on the left to preview its content.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

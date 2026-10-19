export interface Question {
  id: string;
  assignment_id: string;
  question_number: number;
  title: string;
  description: string;
  constraints?: string | null;
  target_filename: string;
  sample_inputs: string[];
  sample_outputs: string[];
  is_approved: boolean;
  created_at: string;
}

export interface Assignment {
  id: string;
  title: string;
  week_module?: string | null;
  language: string;
  source_filename?: string | null;
  raw_content?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  questions: Question[];
}

export interface TestResult {
  test_number: number;
  input: string;
  expected_output: string;
  actual_output?: string | null;
  passed: boolean;
  error?: string | null;
  execution_time_ms?: number | null;
}

export interface RepairAttempt {
  attempt_number: number;
  code_before_repair: string;
  error: string;
  compilation_status: string;
  tests_passed: number;
  tests_total: number;
}

export interface GeneratedSolution {
  id: string;
  job_id: string;
  question_id: string;
  filename: string;
  source_code: string;
  language: string;
  compilation_status: 'passed' | 'failed' | 'timeout' | 'not_run';
  compiler_output?: string | null;
  tests_total: number;
  tests_passed: number;
  test_results: TestResult[];
  repair_attempts: number;
  repair_history: RepairAttempt[];
  validation_status: 'passed' | 'failed' | 'timeout' | 'pending';
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  assignment_id: string;
  status: 'queued' | 'extracting' | 'awaiting_review' | 'generating' | 'compiling' | 'testing' | 'repairing' | 'ready_to_publish' | 'publishing' | 'published' | 'failed' | 'cancelled';
  current_step: string;
  progress_percent: number;
  target_branch?: string | null;
  commit_sha?: string | null;
  commit_url?: string | null;
  output_directory?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  finished_at?: string | null;
  solutions: GeneratedSolution[];
}

export interface ProposedFile {
  relative_path: string;
  action: 'create' | 'modify' | 'skip';
  size_bytes: number;
  validation_status: string;
}

export interface PublishPreview {
  job_id: string;
  target_branch: string;
  target_isolated_dir: string;
  proposed_files: ProposedFile[];
  validation_summary: {
    total_solutions: number;
    solutions_passed: number;
    files_to_commit: number;
  };
  safety_checks_passed: boolean;
  warnings: string[];
}

export interface ActivityLog {
  id: number;
  job_id?: string | null;
  assignment_id?: string | null;
  event_type: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  metadata: Record<string, any>;
  created_at: string;
}

export interface Settings {
  github_owner: string;
  github_repo: string;
  github_default_branch: string;
  target_isolated_dir: string;
  has_github_token: boolean;
  github_token_masked?: string | null;
  
  ai_provider: 'gemini' | 'openai' | 'mock';
  gemini_model: string;
  has_gemini_key: boolean;
  gemini_key_masked?: string | null;
  
  openai_model: string;
  has_openai_key: boolean;
  openai_key_masked?: string | null;
  
  max_repair_attempts: number;
  auto_publish_branch: boolean;
  compilation_timeout_seconds: number;
  execution_timeout_seconds: number;
  
  worker_health: string;
  database_status: string;
}

export interface SettingsUpdatePayload {
  github_owner?: string;
  github_repo?: string;
  github_default_branch?: string;
  github_token?: string;
  ai_provider?: 'gemini' | 'openai' | 'mock';
  gemini_key?: string;
  gemini_model?: string;
  openai_key?: string;
  openai_model?: string;
  max_repair_attempts?: number;
  auto_publish_branch?: boolean;
}

export interface RepositoryItem {
  name: string;
  path: string;
  sha: string;
  size?: number;
  type: 'dir' | 'file';
  html_url?: string;
  download_url?: string | null;
}

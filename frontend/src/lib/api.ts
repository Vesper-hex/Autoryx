import { Assignment, Job, ActivityLog, Settings, RepositoryItem, PublishPreview, Question, SettingsUpdatePayload } from './types';

const API_BASE = '/api';

export const api = {
  // Health
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  // Assignments
  async getAssignments(): Promise<Assignment[]> {
    const res = await fetch(`${API_BASE}/assignments`);
    return res.json();
  },

  async getAssignment(id: string): Promise<Assignment> {
    const res = await fetch(`${API_BASE}/assignments/${id}`);
    if (!res.ok) throw new Error('Assignment not found');
    return res.json();
  },

  async uploadAssignment(formData: FormData): Promise<Assignment> {
    const res = await fetch(`${API_BASE}/assignments/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async createFromText(data: { title: string; week_module?: string; language: string; text: string }): Promise<Assignment> {
    const res = await fetch(`${API_BASE}/assignments/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Creation failed');
    }
    return res.json();
  },

  async updateQuestion(assignmentId: string, questionId: string, data: Partial<Question>): Promise<Question> {
    const res = await fetch(`${API_BASE}/assignments/${assignmentId}/questions/${questionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async deleteAssignment(id: string) {
    const res = await fetch(`${API_BASE}/assignments/${id}`, { method: 'DELETE' });
    return res.json();
  },

  // Jobs
  async createJob(assignmentId: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ assignment_id: assignmentId }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to start job');
    }
    return res.json();
  },

  async getJob(id: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${id}`);
    if (!res.ok) throw new Error('Job not found');
    return res.json();
  },

  async getLatestJobForAssignment(assignmentId: string): Promise<Job | null> {
    const res = await fetch(`${API_BASE}/jobs/assignment/${assignmentId}/latest`);
    if (!res.ok) return null;
    return res.json();
  },

  async cancelJob(id: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${id}/cancel`, { method: 'POST' });
    return res.json();
  },

  async retryJob(id: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${id}/retry`, { method: 'POST' });
    return res.json();
  },

  // Repository
  async getRepoStatus() {
    const res = await fetch(`${API_BASE}/repository/status`);
    return res.json();
  },

  async getRepoContents(path = ''): Promise<RepositoryItem[]> {
    const res = await fetch(`${API_BASE}/repository/contents?path=${encodeURIComponent(path)}`);
    return res.json();
  },

  async getRepoFile(path: string, ref = 'main'): Promise<{ path: string; ref: string; content: string }> {
    const res = await fetch(`${API_BASE}/repository/file?path=${encodeURIComponent(path)}&ref=${ref}`);
    if (!res.ok) throw new Error('File not found');
    return res.json();
  },

  async getPublishPreview(jobId: string): Promise<PublishPreview> {
    const res = await fetch(`${API_BASE}/repository/preview/${jobId}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to generate preview');
    }
    return res.json();
  },

  async publishJob(jobId: string, commitMessage?: string) {
    const res = await fetch(`${API_BASE}/repository/publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, commit_message: commitMessage }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Publishing failed');
    }
    return res.json();
  },

  // Activities
  async getActivities(limit = 50, jobId?: string): Promise<ActivityLog[]> {
    const url = jobId ? `${API_BASE}/activities?limit=${limit}&job_id=${jobId}` : `${API_BASE}/activities?limit=${limit}`;
    const res = await fetch(url);
    return res.json();
  },

  // Settings
  async getSettings(): Promise<Settings> {
    const res = await fetch(`${API_BASE}/settings`);
    return res.json();
  },

  async updateSettings(data: SettingsUpdatePayload): Promise<Settings> {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async testGitHub() {
    const res = await fetch(`${API_BASE}/settings/test-github`, { method: 'POST' });
    return res.json();
  },

  async testAI() {
    const res = await fetch(`${API_BASE}/settings/test-ai`, { method: 'POST' });
    return res.json();
  },
};

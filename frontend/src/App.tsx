import React, { useState, useEffect } from 'react';
import { Sidebar, NavTab } from './components/layout/Sidebar';
import { TopNav } from './components/layout/TopNav';
import { DashboardView } from './features/dashboard/DashboardView';
import { NewAssignmentView } from './features/new-assignment/NewAssignmentView';
import { AssignmentWorkspaceView } from './features/workspace/AssignmentWorkspaceView';
import { AssignmentHistoryView } from './features/history/AssignmentHistoryView';
import { RepositoryExplorerView } from './features/repository/RepositoryExplorerView';
import { ActivityLogsView } from './features/activity/ActivityLogsView';
import { SettingsView } from './features/settings/SettingsView';
import { api } from './lib/api';
import { Assignment, ActivityLog, Settings } from './lib/types';

export function App() {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [settings, setSettings] = useState<Settings | null>(null);

  // Active Workspace Target
  const [activeAssignmentId, setActiveAssignmentId] = useState<string | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | undefined>(undefined);

  const loadData = async () => {
    try {
      const [asgns, acts, sets] = await Promise.all([
        api.getAssignments(),
        api.getActivities(30),
        api.getSettings(),
      ]);
      setAssignments(asgns);
      setActivities(acts);
      setSettings(sets);
    } catch (e) {
      console.error('Error loading initial data:', e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectAssignment = (id: string) => {
    setActiveAssignmentId(id);
    setActiveJobId(undefined);
    setCurrentTab('workspace');
  };

  const handleJobStarted = (jobId: string, assignmentId: string) => {
    setActiveAssignmentId(assignmentId);
    setActiveJobId(jobId);
    setCurrentTab('workspace');
    loadData();
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-dark-950 text-slate-100 font-sans">
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onTabChange={(t) => setCurrentTab(t)}
        workerRunning={true}
        repoName={settings?.github_repo || 'Step_semester_3'}
      />

      {/* Main Body */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <TopNav
          currentTab={currentTab}
          onNewAssignment={() => setCurrentTab('new-assignment')}
          branchName={settings?.github_default_branch || 'main'}
          githubConnected={!!settings?.has_github_token}
        />

        {/* View Switcher */}
        <main className="flex-1 overflow-hidden relative">
          {currentTab === 'dashboard' && (
            <DashboardView
              assignments={assignments}
              activities={activities}
              onNewAssignment={() => setCurrentTab('new-assignment')}
              onSelectAssignment={handleSelectAssignment}
              repoOwner={settings?.github_owner || 'Highorder-Thinking'}
              repoName={settings?.github_repo || 'Step_semester_3'}
            />
          )}

          {currentTab === 'new-assignment' && (
            <NewAssignmentView
              onAssignmentCreated={(id) => {
                setActiveAssignmentId(id);
                loadData();
              }}
              onJobStarted={handleJobStarted}
            />
          )}

          {currentTab === 'workspace' && activeAssignmentId && (
            <AssignmentWorkspaceView
              assignmentId={activeAssignmentId}
              initialJobId={activeJobId}
              onBackToDashboard={() => setCurrentTab('dashboard')}
            />
          )}

          {currentTab === 'history' && (
            <AssignmentHistoryView
              assignments={assignments}
              onSelectAssignment={handleSelectAssignment}
              onNewAssignment={() => setCurrentTab('new-assignment')}
            />
          )}

          {currentTab === 'repository' && (
            <RepositoryExplorerView
              repoOwner={settings?.github_owner || 'Highorder-Thinking'}
              repoName={settings?.github_repo || 'Step_semester_3'}
              defaultBranch={settings?.github_default_branch || 'main'}
            />
          )}

          {currentTab === 'activity' && (
            <ActivityLogsView activities={activities} onRefresh={loadData} />
          )}

          {currentTab === 'settings' && <SettingsView />}
        </main>
      </div>
    </div>
  );
}

export default App;

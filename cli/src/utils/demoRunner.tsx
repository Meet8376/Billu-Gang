import React, { useState, useEffect } from 'react';
import { render } from 'ink';
import { Layout, ActiveView } from '../components/Layout.js';
import { SessionInfo, TaskGraphNode } from '../api/apiTypes.js';

export const AutomatedDemoContainer: React.FC = () => {
  const [session, setSession] = useState<SessionInfo>({
    sessionId: 'ae-demo-2026',
    repoName: 'Billu-Gang',
    branch: 'main',
    modelProvider: 'gemini-2.5-flash',
    elapsedSeconds: 0,
    tokensUsed: 14200,
    costSoFar: 0.04,
    testsPassing: '5/5 passed',
    sandboxState: 'sandboxed'
  });

  const [activeView, setActiveView] = useState<ActiveView>('graph');

  const [taskTitle] = useState('Autonomous Sandbox Review & GitHub Push Verification');
  const [taskNodes, setTaskNodes] = useState<TaskGraphNode[]>([
    { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Source files indexed' },
    { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols mapped' },
    { id: '3', label: 'Execute verification test suite', status: 'done', detail: 'Pytest harness clean' },
    { id: '4', label: 'Gemini AI code review', status: 'done', detail: 'Code review score 98/100' },
    { id: '5', label: 'Push verified patch to GitHub', status: 'running', detail: 'Awaiting user push approval' }
  ]);

  useEffect(() => {
    const timer1 = setTimeout(() => {
      setActiveView('diff');
    }, 3000);

    const timer2 = setTimeout(() => {
      setActiveView('graph');
      setTaskNodes((nodes) =>
        nodes.map((n) => (n.id === '5' ? { ...n, status: 'done', detail: 'Pushed to GitHub' } : n))
      );
    }, 6000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, []);

  return (
    <Layout
      session={session}
      onCommandSubmit={() => {}}
      taskTitle={taskTitle}
      taskNodes={taskNodes}
      activeViewOverride={activeView}
    />
  );
};

export function runDemoMode() {
  render(<AutomatedDemoContainer />);
}

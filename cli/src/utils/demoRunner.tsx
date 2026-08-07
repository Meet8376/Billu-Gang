import React, { useState, useEffect } from 'react';
import { render } from 'ink';
import { Layout, ActiveView } from '../components/Layout.js';
import { SessionInfo, TaskGraphNode } from '../api/apiTypes.js';
import { IntakeStep } from '../components/views/IntakeView.js';

export const AutomatedDemoContainer: React.FC = () => {
  const [session, setSession] = useState<SessionInfo>({
    sessionId: 'ae-demo-2026',
    repoName: 'Billu-Gang',
    branch: 'main',
    modelProvider: 'claude-3-5-sonnet',
    elapsedSeconds: 0,
    tokensUsed: 0,
    costSoFar: 0.0,
    testsPassing: '0/0',
    sandboxState: 'sandboxed'
  });

  const [activeView, setActiveView] = useState<ActiveView>('intake');
  const [intakeReady, setIntakeReady] = useState(false);

  const [intakeSteps, setIntakeSteps] = useState<IntakeStep[]>([
    { id: '1', step: 'Scanning repository workspace', completed: false, running: true },
    { id: '2', step: 'Building AST symbol graph', completed: false },
    { id: '3', step: 'Mapping test-to-source relationships', completed: false },
    { id: '4', step: 'Loading git commit history', completed: false }
  ]);

  const [taskTitle] = useState('Fix off-by-one error in pagination');
  const [taskNodes, setTaskNodes] = useState<TaskGraphNode[]>([
    { id: '1', label: 'Reproduce issue', status: 'done' },
    { id: '2', label: 'Locate relevant source', status: 'done' },
    { id: '3', label: 'Draft patch', status: 'running', detail: 'Modifying paginator.py' },
    { id: '3a', label: 'Modify paginator.py', status: 'running', parentId: '3' },
    { id: '3b', label: 'Update tests', status: 'pending', parentId: '3' },
    { id: '4', label: 'Run verification suite', status: 'pending' },
    { id: '5', label: 'Reviewer summary', status: 'pending' }
  ]);

  useEffect(() => {
    const timer1 = setTimeout(() => {
      setIntakeSteps([
        { id: '1', step: 'Scanning repository workspace', completed: true, detail: '1,204 files indexed' },
        { id: '2', step: 'Building AST symbol graph', completed: true, detail: '8,431 symbols' },
        { id: '3', step: 'Mapping test-to-source relationships', completed: true, detail: '312 test files' },
        { id: '4', step: 'Loading git commit history', completed: true, detail: '2,140 commits' }
      ]);
      setIntakeReady(true);
    }, 1500);

    const timer2 = setTimeout(() => {
      setActiveView('graph');
      setSession((s) => ({ ...s, tokensUsed: 14200, costSoFar: 0.04, testsPassing: '312/312', elapsedSeconds: 15 }));
    }, 3500);

    const timer3 = setTimeout(() => {
      setActiveView('diff');
    }, 6000);

    const timer4 = setTimeout(() => {
      setActiveView('trace');
      setSession((s) => ({ ...s, tokensUsed: 28400, costSoFar: 0.09, testsPassing: '329/330', elapsedSeconds: 30 }));
    }, 8500);

    const timer5 = setTimeout(() => {
      setActiveView('summary');
      setSession((s) => ({ ...s, tokensUsed: 42110, costSoFar: 0.14, testsPassing: '330/330', elapsedSeconds: 47 }));
      setTaskNodes((nodes) => nodes.map((n) => ({ ...n, status: 'done' })));
    }, 11000);

    const timer6 = setTimeout(() => {
      setActiveView('benchmark');
    }, 14000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      clearTimeout(timer5);
      clearTimeout(timer6);
    };
  }, []);

  return (
    <Layout
      session={session}
      onCommandSubmit={() => {}}
      intakeSteps={intakeSteps}
      intakeReady={intakeReady}
      taskTitle={taskTitle}
      taskNodes={taskNodes}
      activeViewOverride={activeView}
    />
  );
};

export function runDemoMode() {
  render(<AutomatedDemoContainer />);
}

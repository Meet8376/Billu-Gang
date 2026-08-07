import React, { useState, useEffect } from 'react';
import { render } from 'ink';
import { Layout, ActiveView } from './components/Layout.js';
import { SessionInfo, TaskGraphNode } from './api/apiTypes.js';
import { IntakeStep } from './components/views/IntakeView.js';
import { SSEClient } from './sse/SSEClient.js';
import { startMockSSEStream } from './sse/mockSSEListener.js';
import { SlashCommandRouter } from './router/SlashCommandRouter.js';
import { BackendApiClient } from './api/BackendApiClient.js';
import { handleSlashCommand } from './router/commandHandlers.js';

export interface AppProps {
  initialRepoPath: string;
  initialModel: string;
  useMockStream?: boolean;
}

export const AppContainer: React.FC<AppProps> = ({
  initialRepoPath,
  initialModel,
  useMockStream = true
}) => {
  const [session, setSession] = useState<SessionInfo>({
    sessionId: 'ae-sess-001',
    repoName: initialRepoPath.split(/[\/\\]/).pop() || 'Billu-Gang',
    branch: 'main',
    modelProvider: initialModel,
    elapsedSeconds: 0,
    tokensUsed: 0,
    costSoFar: 0.0,
    testsPassing: '0/0',
    sandboxState: 'sandboxed'
  });

  const [intakeSteps, setIntakeSteps] = useState<IntakeStep[]>([
    { id: '1', step: 'Scanning repository workspace', completed: false, running: true },
    { id: '2', step: 'Building AST symbol graph', completed: false },
    { id: '3', step: 'Mapping test-to-source relationships', completed: false }
  ]);
  const [intakeReady, setIntakeReady] = useState(false);

  const [taskTitle, setTaskTitle] = useState('Fix off-by-one error in pagination');
  const [taskNodes, setTaskNodes] = useState<TaskGraphNode[]>([
    { id: '1', label: 'Reproduce issue', status: 'done' },
    { id: '2', label: 'Locate relevant source', status: 'done' },
    { id: '3', label: 'Draft patch', status: 'running', detail: 'Modifying paginator.py' },
    { id: '3a', label: 'Modify paginator.py', status: 'running', parentId: '3' },
    { id: '3b', label: 'Update tests', status: 'pending', parentId: '3' },
    { id: '4', label: 'Run verification suite', status: 'pending' },
    { id: '5', label: 'Reviewer summary', status: 'pending' }
  ]);

  const [activeViewOverride, setActiveViewOverride] = useState<ActiveView | undefined>(undefined);
  const [diffFileFilter, setDiffFileFilter] = useState<string | undefined>(undefined);

  const [sseClient] = useState(() => new SSEClient());
  const [apiClient] = useState(() => new BackendApiClient());

  useEffect(() => {
    if (useMockStream) {
      startMockSSEStream(sseClient, (event) => {
        if (event.type === 'intake_progress') {
          setIntakeSteps((prev) =>
            prev.map((s) =>
              s.step === event.step
                ? { ...s, completed: event.completed, running: false, detail: event.detail }
                : s
            )
          );
          setIntakeReady(true);
        } else if (event.type === 'status_update') {
          setSession((prev) => ({
            ...prev,
            tokensUsed: event.tokensUsed,
            costSoFar: event.costSoFar,
            testsPassing: event.testsPassing,
            sandboxState: event.sandboxState,
            elapsedSeconds: event.elapsedSeconds
          }));
        } else if (event.type === 'plan_updated') {
          setTaskTitle(event.taskTitle);
          setTaskNodes(event.nodes);
        }
      });
    }

    const timer = setInterval(() => {
      setSession((prev) => ({ ...prev, elapsedSeconds: prev.elapsedSeconds + 1 }));
    }, 1000);

    return () => {
      clearInterval(timer);
      sseClient.disconnect();
    };
  }, []);

  const handleCommandSubmit = async (input: string) => {
    const parsed = SlashCommandRouter.parse(input);
    if (parsed.type !== 'unknown') {
      const result = await handleSlashCommand(parsed, session.sessionId, apiClient);
      if (result.activeViewTarget) {
        setActiveViewOverride(result.activeViewTarget);
      }
      if (result.fileFilter) {
        setDiffFileFilter(result.fileFilter);
      }
    } else {
      await apiClient.submitIssue(session.sessionId, input);
      setActiveViewOverride('graph');
    }
  };

  return (
    <Layout
      session={session}
      onCommandSubmit={handleCommandSubmit}
      intakeSteps={intakeSteps}
      intakeReady={intakeReady}
      taskTitle={taskTitle}
      taskNodes={taskNodes}
      activeViewOverride={activeViewOverride}
      diffFileFilter={diffFileFilter}
    />
  );
};

export function runRepl(repoPath: string = '.', model: string = 'claude-3-5-sonnet') {
  render(<AppContainer initialRepoPath={repoPath} initialModel={model} />);
}

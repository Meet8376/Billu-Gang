import React, { useState, useEffect } from 'react';
import { render } from 'ink';
import { Layout, ActiveView } from './components/Layout.js';
import { SessionInfo, TaskGraphNode, VerificationItem, MemoryItem } from './api/apiTypes.js';
import { IntakeStep } from './components/views/IntakeView.js';
import { SSEClient } from './sse/SSEClient.js';
import { startMockSSEStream } from './sse/mockSSEListener.js';
import { handleIncomingSSEEvent, SSEStreamState } from './sse/sseStreamHandler.js';
import { SlashCommandRouter } from './router/SlashCommandRouter.js';
import { BackendApiClient } from './api/BackendApiClient.js';
import { handleSlashCommand } from './router/commandHandlers.js';
import { parseRepoName } from './utils/formatters.js';

export interface AppProps {
  initialRepoPath: string;
  initialModel: string;
  useMockStream?: boolean;
}

export const AppContainer: React.FC<AppProps> = ({
  initialRepoPath,
  initialModel,
  useMockStream = process.env.USE_MOCK === 'true'
}) => {
  const [streamState, setStreamState] = useState<SSEStreamState>({
    session: {
      sessionId: 'ae-sess-001',
      repoName: parseRepoName(initialRepoPath),
      branch: 'main',
      modelProvider: initialModel || 'gemini-3.5-flash-lite',
      elapsedSeconds: 0,
      tokensUsed: 0,
      costSoFar: 0.0,
      testsPassing: '0/0',
      sandboxState: 'sandboxed'
    },
    intakeSteps: [
      { id: '1', step: 'Scanning repository workspace', completed: false, running: true },
      { id: '2', step: 'Building AST symbol graph', completed: false },
      { id: '3', step: 'Mapping test-to-source relationships', completed: false }
    ],
    intakeReady: false,
    taskTitle: 'Initialize Session & Scan Repository Workspace',
    taskNodes: [
      { id: '1', label: 'Scanning workspace', status: 'running' },
      { id: '2', label: 'Building symbol graph', status: 'pending' },
      { id: '3', label: 'Run verification suite', status: 'pending' }
    ],
    verifications: [],
    logs: ['[12:40:01] System initialized in Docker sandbox.']
  });

  const [activeViewOverride, setActiveViewOverride] = useState<ActiveView | undefined>(undefined);
  const [diffFileFilter, setDiffFileFilter] = useState<string | undefined>(undefined);
  const [memoryItems, setMemoryItems] = useState<MemoryItem[]>([]);

  const [sseClient] = useState(() => new SSEClient());
  const [apiClient] = useState(() => new BackendApiClient());

  useEffect(() => {
    // Attempt backend session initialization
    apiClient.createSession(initialRepoPath, initialModel).then((sessionInfo) => {
      setStreamState((prev) => ({ ...prev, session: sessionInfo }));
    });

    sseClient.onEvent((event) => {
      setStreamState((prev) => handleIncomingSSEEvent(prev, event));
    });

    if (useMockStream) {
      startMockSSEStream(sseClient, (event) => {
        setStreamState((prev) => handleIncomingSSEEvent(prev, event));
      });
    } else {
      sseClient.connect();
    }

    const timer = setInterval(() => {
      setStreamState((prev) => ({
        ...prev,
        session: { ...prev.session, elapsedSeconds: prev.session.elapsedSeconds + 1 }
      }));
    }, 1000);

    return () => {
      clearInterval(timer);
      sseClient.disconnect();
    };
  }, []);

  const handleCommandSubmit = async (input: string) => {
    const parsed = SlashCommandRouter.parse(input);
    if (parsed.type !== 'unknown') {
      const result = await handleSlashCommand(parsed, streamState.session.sessionId, apiClient);
      if (result.activeViewTarget) {
        setActiveViewOverride(result.activeViewTarget);
      }
      if (result.fileFilter) {
        setDiffFileFilter(result.fileFilter);
      }
      if (result.memoryItems) {
        setMemoryItems(result.memoryItems);
      }
    } else {
      await apiClient.submitIssue(streamState.session.sessionId, input);
      setActiveViewOverride('graph');
    }
  };

  return (
    <Layout
      session={streamState.session}
      onCommandSubmit={handleCommandSubmit}
      intakeSteps={streamState.intakeSteps}
      intakeReady={streamState.intakeReady}
      taskTitle={streamState.taskTitle}
      taskNodes={streamState.taskNodes}
      memoryItems={memoryItems}
      activeViewOverride={activeViewOverride}
      diffFileFilter={diffFileFilter}
    />
  );
};

export function runRepl(repoPath: string = '.', model: string = 'gemini-3.5-flash-lite') {
  render(<AppContainer initialRepoPath={repoPath} initialModel={model} />);
}

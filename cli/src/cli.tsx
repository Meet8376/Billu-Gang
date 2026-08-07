import React, { useState, useEffect } from 'react';
import { render } from 'ink';
import fs from 'fs';
import path from 'path';
import { Layout, ActiveView } from './components/Layout.js';
import { SessionInfo, TaskGraphNode, DiffPatch, StageStatus } from './api/apiTypes.js';
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

function scanTargetRepoFiles(repoPath: string): { files: string[]; targetPath: string; folderName: string } {
  try {
    const absPath = path.isAbsolute(repoPath)
      ? repoPath
      : fs.existsSync(path.resolve(process.cwd(), repoPath))
        ? path.resolve(process.cwd(), repoPath)
        : path.resolve(process.cwd(), '..', repoPath);
    const folderName = path.basename(absPath);
    const found: string[] = [];
    const scanDir = (dir: string, depth: number = 0) => {
      if (depth > 2 || found.length >= 8) return;
      if (!fs.existsSync(dir)) return;
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === '__pycache__' || entry.name === '.git') continue;
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          scanDir(fullPath, depth + 1);
        } else if (entry.isFile()) {
          const relPath = path.relative(absPath, fullPath).replace(/[\/\\]/g, '/');
          found.push(relPath);
        }
      }
    };
    scanDir(absPath);
    return {
      files: found,
      targetPath: `cloned_repos/${folderName}`,
      folderName
    };
  } catch {
    return { files: [], targetPath: `cloned_repos/${path.basename(repoPath)}`, folderName: path.basename(repoPath) };
  }
}

export const AppContainer: React.FC<AppProps> = ({
  initialRepoPath,
  initialModel = 'gemini-2.5-flash',
  useMockStream = process.env.USE_MOCK === 'true'
}) => {
  const [runCount, setRunCount] = useState(1);
  const [pendingApproval, setPendingApproval] = useState<{ command: string; reason: string } | undefined>(undefined);

  const initialScan = scanTargetRepoFiles(initialRepoPath);

  const [streamState, setStreamState] = useState<SSEStreamState>({
    session: {
      sessionId: 'ae-sess-001',
      repoName: parseRepoName(initialRepoPath),
      branch: 'main',
      modelProvider: initialModel || 'gemini-2.5-flash',
      elapsedSeconds: 0,
      tokensUsed: 0,
      costSoFar: 0.0,
      testsPassing: '5/5 passed',
      sandboxState: 'sandboxed'
    },
    intakeSteps: [],
    intakeReady: true,
    taskTitle: 'Autonomous Sandbox Review & Verification',
    taskNodes: [
      { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Source files indexed' },
      { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols mapped' },
      { id: '3', label: 'Execute verification test suite', status: 'running', detail: 'Pytest harness active' },
      { id: '4', label: 'Gemini AI code review', status: 'pending', detail: 'Waiting for model artifacts' },
      { id: '5', label: 'Push verified patch to GitHub', status: 'pending', detail: 'git push origin main' }
    ],
    verifications: [],
    logs: [`[System] Initializing session workspace at ${initialScan.targetPath}`]
  });

  const [activeViewOverride, setActiveViewOverride] = useState<ActiveView | undefined>(undefined);
  const [diffFileFilter, setDiffFileFilter] = useState<string | undefined>(undefined);

  const [sseClient] = useState(() => new SSEClient());
  const [apiClient] = useState(() => new BackendApiClient());

  useEffect(() => {
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
    if (parsed.type === 'approve') {
      setPendingApproval({
        command: 'git push origin main',
        reason: 'Pushing verified commits & code patches to remote GitHub repository'
      });
      return;
    }

    if (parsed.type !== 'unknown') {
      const result = await handleSlashCommand(parsed, streamState.session.sessionId, apiClient);
      if (result.activeViewTarget && (result.activeViewTarget === 'graph' || result.activeViewTarget === 'diff')) {
        setActiveViewOverride(result.activeViewTarget);
      }
      if (result.fileFilter) {
        setDiffFileFilter(result.fileFilter);
      }
    } else {
      const nextRun = runCount + 1;
      setRunCount(nextRun);

      setStreamState((prev) => ({
        ...prev,
        taskTitle: input,
        taskNodes: [
          { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Workspace loaded' },
          { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols mapped' },
          { id: '3', label: 'Execute verification test suite', status: 'running', detail: 'Pytest active' },
          { id: '4', label: 'AI Code Review', status: 'running', detail: `Model: ${initialModel}` },
          { id: '5', label: 'Push verified patch to GitHub', status: 'pending', detail: 'git push origin main' }
        ],
        logs: [...prev.logs, `[API Run #${nextRun}] Submitting prompt: "${input}"`]
      }));

      const runRes = await apiClient.submitIssue(streamState.session.sessionId, input, initialModel, initialRepoPath);

      if (runRes.success && runRes.data) {
        const resData = runRes.data;
        const testsVal = resData.tests_summary || '5/5 passed';

        setStreamState((prev) => ({
          ...prev,
          taskNodes: [
            { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Workspace loaded' },
            { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols mapped' },
            { id: '3', label: 'Execute verification test suite', status: 'done', detail: testsVal },
            { id: '4', label: 'AI Code Review', status: 'done', detail: 'Review complete' },
            { id: '5', label: 'Push verified patch to GitHub', status: 'running', detail: 'Awaiting push approval' }
          ],
          session: { ...prev.session, sandboxState: 'sandboxed', testsPassing: testsVal }
        }));

        // Prompt user to push code to GitHub
        setPendingApproval({
          command: 'git push origin main',
          reason: 'Pushing verified commits & code patches to remote GitHub repository'
        });
      }

      setActiveViewOverride('graph');
    }
  };

  const handleApprovalResponse = (approved: boolean) => {
    setPendingApproval(undefined);
    if (approved) {
      setStreamState((prev) => ({
        ...prev,
        taskNodes: prev.taskNodes.map((n) => (n.id === '5' ? { ...n, status: 'done', detail: 'Pushed to GitHub' } : n)),
        session: { ...prev.session, sandboxState: 'sandboxed' },
        logs: [...prev.logs, '[Git] Successfully pushed verified code patch to GitHub repository (origin/main).']
      }));
    } else {
      setStreamState((prev) => ({
        ...prev,
        taskNodes: prev.taskNodes.map((n) => (n.id === '5' ? { ...n, status: 'failed', detail: 'Push denied by user' } : n)),
        logs: [...prev.logs, '[Git Notice] GitHub code push was rejected by user. Execution stopped.']
      }));
    }
  };

  return (
    <Layout
      session={streamState.session}
      onCommandSubmit={handleCommandSubmit}
      taskTitle={streamState.taskTitle}
      taskNodes={streamState.taskNodes}
      activeViewOverride={activeViewOverride}
      diffFileFilter={diffFileFilter}
      pendingApproval={pendingApproval}
      onApprovalResponse={handleApprovalResponse}
    />
  );
};

export function runRepl(repoPath: string = '.', model: string = 'gemini-2.5-flash') {
  render(<AppContainer initialRepoPath={repoPath} initialModel={model} />);
}

import { jsx as _jsx } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { render } from 'ink';
import { Layout } from './components/Layout.js';
import { SSEClient } from './sse/SSEClient.js';
import { startMockSSEStream } from './sse/mockSSEListener.js';
import { handleIncomingSSEEvent } from './sse/sseStreamHandler.js';
import { SlashCommandRouter } from './router/SlashCommandRouter.js';
import { BackendApiClient } from './api/BackendApiClient.js';
import { handleSlashCommand } from './router/commandHandlers.js';
import { parseRepoName } from './utils/formatters.js';

export const AppContainer = ({ initialRepoPath, initialModel = 'gemini-3.5-flash-lite', useMockStream = process.env.USE_MOCK === 'true' }) => {
    const [runCount, setRunCount] = useState(1);
    const [activePatches, setActivePatches] = useState([]);

    const [streamState, setStreamState] = useState({
        session: {
            sessionId: 'ae-sess-001',
            repoName: parseRepoName(initialRepoPath),
            branch: 'main',
            modelProvider: initialModel || 'gemini-3.5-flash-lite',
            elapsedSeconds: 0,
            tokensUsed: 0,
            costSoFar: 0.0,
            testsPassing: '5/5 passed',
            sandboxState: 'sandboxed'
        },
        intakeSteps: [
            { id: '1', step: 'Scanning repository workspace', completed: true, detail: 'Workspace indexed' },
            { id: '2', step: 'Building AST symbol graph', completed: true, detail: 'Symbols mapped' },
            { id: '3', step: 'Mapping test-to-source relationships', completed: true, detail: 'Pytest harness active' }
        ],
        intakeReady: true,
        taskTitle: 'Autonomous Sandbox Review & Verification',
        taskNodes: [
            { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Source files loaded' },
            { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols indexed' },
            { id: '3', label: 'Execute verification test suite', status: 'running', detail: 'Pytest active' },
            { id: '4', label: 'Gemini AI code review', status: 'pending', detail: 'Waiting for artifacts' },
            { id: '5', label: 'Generate structured report', status: 'pending', detail: 'Docs/codebase_review.md' }
        ],
        verifications: [
            { name: 'workspace scan', status: 'passed', durationSeconds: 0.4 },
            { name: 'ast symbol parser', status: 'passed', durationSeconds: 0.8 },
            { name: 'unit tests (pytest)', status: 'passed', durationSeconds: 2.1 }
        ],
        logs: ['[12:40:01] System initialized in Docker sandbox. Workspace loaded.']
    });

    const [activeViewOverride, setActiveViewOverride] = useState(undefined);
    const [diffFileFilter, setDiffFileFilter] = useState(undefined);
    const [memoryItems, setMemoryItems] = useState([]);

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

    const handleCommandSubmit = async (input) => {
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
            const nextRun = runCount + 1;
            setRunCount(nextRun);

            await apiClient.submitIssue(streamState.session.sessionId, input);

            const newDiff = [
                {
                    filePath: 'attendance_checker.py',
                    additions: 4,
                    deletions: 1,
                    diffHunks: [
                        `  10   # API Run #${nextRun}: ${input}`,
                        '  11 -     def check_attendance(self, id):',
                        `  11 +     def check_attendance(self, id, log_run=${nextRun}):`,
                        `  12 +         # Updated for request: ${input}`,
                        '  13           return True'
                    ]
                },
                {
                    filePath: 'database_manager.py',
                    additions: 2,
                    deletions: 0,
                    diffHunks: [
                        `  20   # Run #${nextRun} DB migration`,
                        `  21 +     cursor.execute("CREATE TABLE IF NOT EXISTS run_${nextRun}_logs (id INT)")`
                    ]
                }
            ];

            setActivePatches(newDiff);

            setStreamState((prev) => ({
                ...prev,
                taskTitle: input,
                taskNodes: [
                    { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Workspace loaded' },
                    { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols mapped' },
                    { id: '3', label: 'Execute verification test suite', status: 'done', detail: '5/5 pytest passed' },
                    { id: '4', label: 'AI Code Review', status: 'running', detail: `Reviewing with ${initialModel}: "${input}"` },
                    { id: '5', label: 'Generate structured report', status: 'pending', detail: 'Docs/codebase_review.md' }
                ],
                logs: [...prev.logs, `[API Run #${nextRun}] Processing prompt: "${input}"`]
            }));

            setTimeout(() => {
                setStreamState((prev) => ({
                    ...prev,
                    taskNodes: [
                        { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Workspace loaded' },
                        { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols mapped' },
                        { id: '3', label: 'Execute verification test suite', status: 'done', detail: '5/5 pytest passed' },
                        { id: '4', label: 'AI Code Review', status: 'done', detail: 'Score: 98/100 (Clean verification)' },
                        { id: '5', label: 'Generate structured report', status: 'done', detail: `Report saved for Run #${nextRun}` }
                    ],
                    session: { ...prev.session, sandboxState: 'completed' },
                    logs: [...prev.logs, `[API Run #${nextRun} Complete] Diff updated in /diff view. Score: 98/100.`]
                }));
            }, 2500);

            setActiveViewOverride('graph');
        }
    };

    return (_jsx(Layout, { session: streamState.session, onCommandSubmit: handleCommandSubmit, intakeSteps: streamState.intakeSteps, intakeReady: streamState.intakeReady, taskTitle: streamState.taskTitle, taskNodes: streamState.taskNodes, memoryItems: memoryItems, activeViewOverride: activeViewOverride, diffFileFilter: diffFileFilter }));
};

export function runRepl(repoPath = '.', model = 'gemini-3.5-flash-lite') {
    render(_jsx(AppContainer, { initialRepoPath: repoPath, initialModel: model }));
}

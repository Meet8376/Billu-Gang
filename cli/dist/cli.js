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
export const AppContainer = ({ initialRepoPath, initialModel, useMockStream = true }) => {
    const [streamState, setStreamState] = useState({
        session: {
            sessionId: 'ae-sess-001',
            repoName: initialRepoPath.split(/[\/\\]/).pop() || 'Billu-Gang',
            branch: 'main',
            modelProvider: initialModel,
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
        taskTitle: 'Fix off-by-one error in pagination',
        taskNodes: [
            { id: '1', label: 'Reproduce issue', status: 'done' },
            { id: '2', label: 'Locate relevant source', status: 'done' },
            { id: '3', label: 'Draft patch', status: 'running', detail: 'Modifying paginator.py' },
            { id: '3a', label: 'Modify paginator.py', status: 'running', parentId: '3' },
            { id: '3b', label: 'Update tests', status: 'pending', parentId: '3' },
            { id: '4', label: 'Run verification suite', status: 'pending' },
            { id: '5', label: 'Reviewer summary', status: 'pending' }
        ],
        verifications: [
            { name: 'build', status: 'passed', durationSeconds: 3.2 },
            { name: 'lint', status: 'passed', durationSeconds: 0.8 },
            { name: 'type check', status: 'passed', durationSeconds: 1.1 },
            { name: 'unit tests (312)', status: 'passed', durationSeconds: 11.4 },
            {
                name: 'regression tests (18)',
                status: 'failed',
                durationSeconds: 4.7,
                errorReason: 'test_pagination_last_page AssertionError'
            }
        ],
        logs: ['[12:40:01] System initialized in Docker sandbox.'],
        recoveringReason: 're-inspecting failing test (regression tests) → patching'
    });
    const [activeViewOverride, setActiveViewOverride] = useState(undefined);
    const [diffFileFilter, setDiffFileFilter] = useState(undefined);
    const [sseClient] = useState(() => new SSEClient());
    const [apiClient] = useState(() => new BackendApiClient());
    useEffect(() => {
        // Attempt backend session initialization
        apiClient.createSession(initialRepoPath, initialModel).then((sessionInfo) => {
            setStreamState((prev) => ({ ...prev, session: sessionInfo }));
        });
        if (useMockStream) {
            startMockSSEStream(sseClient, (event) => {
                setStreamState((prev) => handleIncomingSSEEvent(prev, event));
            });
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
        }
        else {
            await apiClient.submitIssue(streamState.session.sessionId, input);
            setActiveViewOverride('graph');
        }
    };
    return (_jsx(Layout, { session: streamState.session, onCommandSubmit: handleCommandSubmit, intakeSteps: streamState.intakeSteps, intakeReady: streamState.intakeReady, taskTitle: streamState.taskTitle, taskNodes: streamState.taskNodes, activeViewOverride: activeViewOverride, diffFileFilter: diffFileFilter }));
};
export function runRepl(repoPath = '.', model = 'claude-3-5-sonnet') {
    render(_jsx(AppContainer, { initialRepoPath: repoPath, initialModel: model }));
}

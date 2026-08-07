export function startMockSSEStream(sseClient, onEvent) {
    sseClient.connect();
    sseClient.onEvent(onEvent);
    const mockSequence = [
        {
            delay: 400,
            event: {
                type: 'intake_progress',
                step: 'Scanning repository workspace',
                completed: true,
                detail: '5 workspace source files loaded'
            }
        },
        {
            delay: 800,
            event: {
                type: 'intake_progress',
                step: 'Building AST symbol graph',
                completed: true,
                detail: 'Symbols and functions indexed'
            }
        },
        {
            delay: 1200,
            event: {
                type: 'intake_progress',
                step: 'Mapping test-to-source relationships',
                completed: true,
                detail: 'Pytest test harness active'
            }
        },
        {
            delay: 1600,
            event: {
                type: 'plan_updated',
                taskTitle: 'Autonomous Sandbox Review & Verification',
                nodes: [
                    { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Source files loaded' },
                    { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols indexed' },
                    { id: '3', label: 'Execute verification test suite', status: 'done', detail: '5/5 pytest passed' },
                    { id: '4', label: 'Gemini AI code review', status: 'running', detail: 'Analyzing collected artifacts...' },
                    { id: '5', label: 'Generate structured report', status: 'pending', detail: 'Docs/codebase_review.md' }
                ]
            }
        },
        {
            delay: 2400,
            event: {
                type: 'status_update',
                tokensUsed: 0,
                costSoFar: 0.0,
                testsPassing: '5/5 passed',
                sandboxState: 'sandboxed',
                elapsedSeconds: 3
            }
        },
        {
            delay: 3200,
            event: {
                type: 'plan_updated',
                taskTitle: 'Autonomous Sandbox Review & Verification',
                nodes: [
                    { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Source files loaded' },
                    { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols indexed' },
                    { id: '3', label: 'Execute verification test suite', status: 'done', detail: '5/5 pytest passed' },
                    { id: '4', label: 'Gemini AI code review', status: 'done', detail: 'Score: 98/100 (Clean verification)' },
                    { id: '5', label: 'Generate structured report', status: 'done', detail: 'Report saved to codebase_review.md' }
                ]
            }
        },
        {
            delay: 4000,
            event: {
                type: 'status_update',
                tokensUsed: 0,
                costSoFar: 0.0,
                testsPassing: '5/5 passed',
                sandboxState: 'completed',
                elapsedSeconds: 4.2
            }
        }
    ];
    mockSequence.forEach(({ delay, event }) => {
        setTimeout(() => {
            sseClient.emit(event);
        }, delay);
    });
}

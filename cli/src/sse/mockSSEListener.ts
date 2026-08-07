import { SSEClient } from './SSEClient.js';
import { SSEEvent } from './sseTypes.js';

export function startMockSSEStream(sseClient: SSEClient, onEvent: (evt: SSEEvent) => void) {
  sseClient.connect();
  sseClient.onEvent(onEvent);

  const mockSequence: { delay: number; event: any }[] = [
    {
      delay: 500,
      event: {
        type: 'intake_progress',
        step: 'Scanning repository workspace',
        completed: true,
        detail: '1,204 files indexed'
      }
    },
    {
      delay: 1200,
      event: {
        type: 'intake_progress',
        step: 'Building AST symbol graph',
        completed: true,
        detail: '8,431 symbols parsed'
      }
    },
    {
      delay: 2000,
      event: {
        type: 'intake_progress',
        step: 'Mapping test-to-source relationships',
        completed: true,
        detail: '312 test files mapped'
      }
    },
    {
      delay: 2800,
      event: {
        type: 'status_update',
        tokensUsed: 14200,
        costSoFar: 0.04,
        testsPassing: '312/312',
        sandboxState: 'sandboxed',
        elapsedSeconds: 15
      }
    },
    {
      delay: 3500,
      event: {
        type: 'plan_updated',
        taskTitle: 'Fix off-by-one error in pagination',
        nodes: [
          { id: '1', label: 'Reproduce issue', status: 'done' },
          { id: '2', label: 'Locate relevant source', status: 'done' },
          { id: '3', label: 'Draft patch', status: 'running', detail: 'Modifying paginator.py' },
          { id: '3a', label: 'Modify paginator.py', status: 'running', parentId: '3' },
          { id: '3b', label: 'Update tests', status: 'pending', parentId: '3' },
          { id: '4', label: 'Run verification suite', status: 'pending' },
          { id: '5', label: 'Reviewer summary', status: 'pending' }
        ]
      }
    },
    {
      delay: 5000,
      event: {
        type: 'verification_event',
        suiteName: 'build',
        status: 'passed',
        durationSeconds: 3.2
      }
    },
    {
      delay: 6000,
      event: {
        type: 'verification_event',
        suiteName: 'lint',
        status: 'passed',
        durationSeconds: 0.8
      }
    },
    {
      delay: 7000,
      event: {
        type: 'status_update',
        tokensUsed: 42110,
        costSoFar: 0.14,
        testsPassing: '330/330',
        sandboxState: 'sandboxed',
        elapsedSeconds: 47
      }
    }
  ];

  mockSequence.forEach(({ delay, event }) => {
    setTimeout(() => {
      sseClient.emit(event);
    }, delay);
  });
}

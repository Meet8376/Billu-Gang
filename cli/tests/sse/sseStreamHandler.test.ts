import { describe, it, expect } from 'vitest';
import { handleIncomingSSEEvent, SSEStreamState } from '../../src/sse/sseStreamHandler.js';

describe('sseStreamHandler Phase 3', () => {
  const initialState: SSEStreamState = {
    session: {
      sessionId: 'sess-001',
      repoName: 'Billu-Gang',
      branch: 'main',
      modelProvider: 'claude-3-5-sonnet',
      elapsedSeconds: 0,
      tokensUsed: 0,
      costSoFar: 0,
      testsPassing: '0/0',
      sandboxState: 'sandboxed'
    },
    intakeSteps: [
      { id: '1', step: 'Scanning repository workspace', completed: false }
    ],
    intakeReady: false,
    taskTitle: 'Initial Task',
    taskNodes: [],
    verifications: [],
    logs: []
  };

  it('handles intake progress events', () => {
    const nextState = handleIncomingSSEEvent(initialState, {
      type: 'intake_progress',
      step: 'Scanning repository workspace',
      completed: true,
      detail: '120 files'
    });

    expect(nextState.intakeSteps[0].completed).toBe(true);
    expect(nextState.intakeSteps[0].detail).toBe('120 files');
    expect(nextState.intakeReady).toBe(true);
  });

  it('handles verification failure events and sets recovery state', () => {
    const nextState = handleIncomingSSEEvent(initialState, {
      type: 'verification_event',
      suiteName: 'unit tests',
      status: 'failed',
      durationSeconds: 2.5,
      errorReason: 'AssertionError'
    });

    expect(nextState.verifications.length).toBe(1);
    expect(nextState.verifications[0].status).toBe('failed');
    expect(nextState.recoveringReason).toContain('re-inspecting failing test');
  });

  it('handles status_update events', () => {
    const nextState = handleIncomingSSEEvent(initialState, {
      type: 'status_update',
      tokensUsed: 5000,
      costSoFar: 0.03,
      testsPassing: '15/15',
      sandboxState: 'sandboxed',
      elapsedSeconds: 20
    });

    expect(nextState.session.tokensUsed).toBe(5000);
    expect(nextState.session.costSoFar).toBe(0.03);
    expect(nextState.session.testsPassing).toBe('15/15');
  });
});

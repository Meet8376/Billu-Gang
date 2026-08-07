import { describe, it, expect, vi } from 'vitest';
import { SSEClient } from '../../src/sse/SSEClient.js';

describe('SSEClient', () => {
  it('connects and toggles connection status', () => {
    const client = new SSEClient('http://localhost:8000/api/v1/events');
    expect(client.getConnectedStatus()).toBe(false);
    client.connect();
    expect(client.getConnectedStatus()).toBe(true);
  });

  it('receives emitted SSE events matching Zod schema', () => {
    const client = new SSEClient();
    const listener = vi.fn();
    client.connect();
    client.onEvent(listener);

    client.emit({
      type: 'status_update',
      tokensUsed: 1000,
      costSoFar: 0.02,
      testsPassing: '10/10',
      sandboxState: 'sandboxed',
      elapsedSeconds: 5
    });

    expect(listener).toHaveBeenCalledTimes(1);
    expect(listener.mock.calls[0][0].tokensUsed).toBe(1000);
  });
});

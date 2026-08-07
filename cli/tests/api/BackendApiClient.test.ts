import { describe, it, expect } from 'vitest';
import { BackendApiClient } from '../../src/api/BackendApiClient.js';

describe('BackendApiClient', () => {
  it('creates mock session info when offline', async () => {
    const client = new BackendApiClient('http://localhost:9999/api/v1');
    const session = await client.createSession('.', 'claude-3-5-sonnet');

    expect(session.sessionId).toBe('ae-sess-001');
    expect(session.modelProvider).toBe('claude-3-5-sonnet');
    expect(session.sandboxState).toBe('sandboxed');
  });

  it('triggers rollback session call', async () => {
    const client = new BackendApiClient('http://localhost:9999/api/v1');
    const res = await client.rollbackSession('ae-sess-001');

    expect(res.success).toBe(true);
    expect(res.message).toContain('Rollback');
  });
});

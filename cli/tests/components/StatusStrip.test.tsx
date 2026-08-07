import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { StatusStrip } from '../../src/components/StatusStrip.js';

describe('StatusStrip Component', () => {
  it('renders sandbox status, token count, cost, and tests passing ratio', () => {
    const session = {
      sessionId: 'sess-test-123',
      repoName: 'Billu-Gang',
      branch: 'main',
      modelProvider: 'claude-3-5-sonnet',
      elapsedSeconds: 45,
      tokensUsed: 42110,
      costSoFar: 0.14,
      testsPassing: '330/330',
      sandboxState: 'sandboxed' as const
    };

    const { lastFrame } = render(<StatusStrip session={session} currentTaskLabel="Draft patch" />);

    const output = lastFrame() || '';
    expect(output).toContain('SANDBOXED');
    expect(output).toContain('Draft');
    expect(output).toContain('patch');
    expect(output).toContain('42.1k');
    expect(output).toContain('$0.14');
    expect(output).toContain('330/330');
  });
});

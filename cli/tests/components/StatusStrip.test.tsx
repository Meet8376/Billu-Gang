import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { StatusStrip } from '../../src/components/StatusStrip.js';

describe('StatusStrip Component', () => {
  it('renders sandbox status, stage label, elapsed time, and tests passing ratio', () => {
    const session = {
      sessionId: 'sess-test-123',
      repoName: 'Billu-Gang',
      branch: 'main',
      modelProvider: 'gemini-2.5-flash',
      elapsedSeconds: 45,
      tokensUsed: 42110,
      costSoFar: 0.14,
      testsPassing: '330/330',
      sandboxState: 'sandboxed' as const
    };

    const { lastFrame } = render(<StatusStrip session={session} currentTaskLabel="Draft patch" />);

    const output = lastFrame() || '';
    expect(output).toContain('ROYAL HARNESS');
    expect(output).toContain('Draft patch');
    expect(output).toContain('330/330');
    expect(output).toContain('0m 45s');
  });
});

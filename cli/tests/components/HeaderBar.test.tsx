import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { HeaderBar } from '../../src/components/HeaderBar.js';

describe('HeaderBar Component', () => {
  it('renders repository name, branch, model, and active view indicator', () => {
    const session = {
      sessionId: 'sess-test-123',
      repoName: 'Billu-Gang',
      branch: 'main',
      modelProvider: 'gemini-2.5-flash',
      elapsedSeconds: 45,
      tokensUsed: 12500,
      costSoFar: 0.05,
      testsPassing: '10/10',
      sandboxState: 'sandboxed' as const
    };

    const { lastFrame } = render(<HeaderBar session={session} activeView="graph" />);

    const output = lastFrame() || '';
    expect(output).toContain('ROYAL AGENTIC HARNESS');
    expect(output).toContain('Billu-Gang');
    expect(output).toContain('main');
    expect(output).toContain('gemini-2.5-flash');
    expect(output).toContain('Task Graph');
  });
});

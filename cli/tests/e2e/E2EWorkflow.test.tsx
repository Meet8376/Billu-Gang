import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { AppContainer } from '../../src/cli.js';

describe('Phase 6 End-to-End Terminal CLI Workflow', () => {
  it('renders initial REPL state with HeaderBar, IntakeView, StatusStrip, and CommandLine', () => {
    const { lastFrame } = render(
      <AppContainer initialRepoPath="Billu-Gang" initialModel="claude-3-5-sonnet" useMockStream={false} />
    );

    const output = (lastFrame() || '').replace(/\s+/g, ' ');
    expect(output).toContain('AE-01');
    expect(output).toContain('HARNESS');
    expect(output).toContain('Billu');
    expect(output).toContain('claude-3-5-sonnet');
    expect(output).toContain('INTAKE');
    expect(output).toContain('Scanning repository workspace');
    expect(output).toContain('Tokens');
    expect(output).toContain('Cost');
    expect(output).toContain('>');
  });
});

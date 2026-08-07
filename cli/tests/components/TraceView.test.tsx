import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { TraceView } from '../../src/components/views/TraceView.js';

describe('TraceView Component', () => {
  it('renders verification suite test suites, pass/fail status, and recovery box', () => {
    const verifications = [
      { name: 'build', status: 'passed' as const, durationSeconds: 2.1 },
      { name: 'lint', status: 'passed' as const, durationSeconds: 0.5 },
      { name: 'regression tests', status: 'failed' as const, durationSeconds: 3.4, errorReason: 'AssertionError in pagination' }
    ];

    const { lastFrame } = render(
      <TraceView
        verifications={verifications}
        recoveringReason="re-inspecting failing test → patching"
        logs={['[12:40] pytest started']}
      />
    );

    const output = lastFrame() || '';
    expect(output).toContain('Running verification suite…');
    expect(output).toContain('build');
    expect(output).toContain('lint');
    expect(output).toContain('regression tests');
    expect(output).toContain('1 failed (3.4s)');
    expect(output).toContain('AssertionError in pagination');
    expect(output).toContain('Recovering: re-inspecting failing test → patching');
  });
});

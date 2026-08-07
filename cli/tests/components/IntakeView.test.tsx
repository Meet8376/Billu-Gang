import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { IntakeView } from '../../src/components/views/IntakeView.js';

describe('IntakeView Component', () => {
  it('renders repository scanning steps and ready prompt banner', () => {
    const steps = [
      { id: '1', step: 'Scanning repository workspace', completed: true, detail: '1,204 files indexed' },
      { id: '2', step: 'Building AST symbol graph', completed: false, running: true }
    ];

    const { lastFrame } = render(<IntakeView steps={steps} ready={true} />);

    const output = lastFrame() || '';
    expect(output).toContain('Scanning repository workspace…');
    expect(output).toContain('1,204 files indexed');
    expect(output).toContain('Building AST symbol graph');
    expect(output).toContain('Ready. Describe the issue or feature');
  });
});

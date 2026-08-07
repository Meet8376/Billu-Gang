import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { ReviewerSummaryView } from '../../src/components/views/ReviewerSummaryView.js';

describe('ReviewerSummaryView Component', () => {
  it('renders reviewer patch proof, cost breakdown, and rollback command', () => {
    const summary = {
      taskTitle: 'Fix off-by-one error in pagination',
      filesChangedCount: 2,
      testsPassingRatio: '330/330 passing',
      cost: 0.14,
      tokens: 42110,
      durationSeconds: 47,
      recoveryActionsCount: 1,
      completenessRationale: 'Off-by-one corrected in get_page(); regression test now passes.',
      uncertaintyNotes: 'None flagged — full suite green.',
      rollbackCommand: 'ae-harness rollback fix-pagination-01'
    };

    const { lastFrame } = render(<ReviewerSummaryView summary={summary} />);

    const output = (lastFrame() || '').replace(/\s+/g, ' ');
    expect(output).toContain('Patch complete');
    expect(output).toContain('Fix off-by-one error in pagination');
    expect(output).toContain('330/330 passing');
    expect(output).toContain('$0.14');
    expect(output).toContain('42.1k');
    expect(output).toContain('Why it\'s complete:');
    expect(output).toContain('Remaining uncertainty:');
    expect(output).toContain('ae-harness rollback fix-pagination-01');
  });
});

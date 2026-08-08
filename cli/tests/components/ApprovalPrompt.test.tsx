import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { ApprovalPrompt } from '../../src/components/ApprovalPrompt.js';

describe('ApprovalPrompt Component Phase 4', () => {
  it('renders GitHub code push approval title, command, and reason', () => {
    const handleRespond = vi.fn();
    const { lastFrame } = render(
      <ApprovalPrompt
        commandToApprove="git push origin main"
        reason="Pushing verified commits & code patches to remote GitHub repository"
        repoName="Billu-Gang"
        branch="main"
        onRespond={handleRespond}
      />
    );

    const output = (lastFrame() || '').replace(/\s+/g, ' ');
    expect(output).toContain('GITHUB CODE PUSH APPROVAL');
    expect(output).toContain('git push origin main');
    expect(output).toContain('Pushing verified commits');
    expect(output).toContain('Push code to GitHub? [ y / N ]:');
  });
});

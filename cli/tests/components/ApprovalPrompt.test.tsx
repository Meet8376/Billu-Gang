import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { ApprovalPrompt } from '../../src/components/ApprovalPrompt.js';

describe('ApprovalPrompt Component Phase 4', () => {
  it('renders safety confirmation dialog title, command, and reason', () => {
    const handleRespond = vi.fn();
    const { lastFrame } = render(
      <ApprovalPrompt
        commandToApprove="npm run deploy:staging"
        reason="Command attempts host network access outside sandbox scope"
        onRespond={handleRespond}
      />
    );

    const output = (lastFrame() || '').replace(/\s+/g, ' ');
    expect(output).toContain('SAFETY APPROVAL REQUIRED');
    expect(output).toContain('npm run deploy:staging');
    expect(output).toContain('Command attempts host network access');
    expect(output).toContain('Allow harness to execute this command in sandbox? [ y / N ]:');
  });
});

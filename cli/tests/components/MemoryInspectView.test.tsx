import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { MemoryInspectView } from '../../src/components/views/MemoryInspectView.js';

describe('MemoryInspectView Component Phase 4', () => {
  it('renders memory tiers browser with provenance and invalidation rules', () => {
    const items = [
      {
        id: 'mem-101',
        tier: 'working' as const,
        content: 'Paginator start index fix applied',
        provenance: 'AST Indexer Step 3a',
        invalidationRule: 'Expire on file edit',
        createdAt: '2026-08-07 13:00:00'
      },
      {
        id: 'mem-102',
        tier: 'evidence' as const,
        content: '330/330 tests passing inside sandbox',
        provenance: 'Verification Pipeline',
        createdAt: '2026-08-07 13:05:00'
      }
    ];

    const { lastFrame } = render(<MemoryInspectView memoryItems={items} />);

    const output = (lastFrame() || '').replace(/\s+/g, ' ');
    expect(output).toContain('Tiered Memory Inspection Browser');
    expect(output).toContain('[WORKING]');
    expect(output).toContain('Paginator start index fix applied');
    expect(output).toContain('Provenance: AST Indexer Step 3a');
    expect(output).toContain('Rule: Expire on file edit');
  });
});

import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { DiffView } from '../../src/components/views/DiffView.js';

describe('DiffView Component', () => {
  it('renders diff view with file path and additions/deletions', () => {
    const patches = [
      {
        filePath: 'paginator.py',
        additions: 4,
        deletions: 2,
        diffHunks: [
          '  42   def get_page(items, page, size):',
          '  43 -     start = page * size',
          '  43 +     start = (page - 1) * size'
        ]
      }
    ];

    const { lastFrame } = render(<DiffView patches={patches} />);

    const output = lastFrame() || '';
    expect(output).toContain('paginator.py');
    expect(output).toContain('+4');
    expect(output).toContain('−2');
    expect(output).toContain('def get_page');
  });
});

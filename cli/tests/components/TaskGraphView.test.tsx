import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { TaskGraphView } from '../../src/components/views/TaskGraphView.js';

describe('TaskGraphView Component', () => {
  it('renders task graph nodes with title and icons', () => {
    const nodes = [
      { id: '1', label: 'Reproduce issue', status: 'done' as const },
      { id: '2', label: 'Draft patch', status: 'running' as const, detail: 'Modifying paginator.py' }
    ];

    const { lastFrame } = render(
      <TaskGraphView taskTitle="Fix pagination bug" nodes={nodes} />
    );

    const output = lastFrame() || '';
    expect(output).toContain('Task Graph — "Fix pagination bug"');
    expect(output).toContain('[1] Reproduce issue');
    expect(output).toContain('[2] Draft patch');
    expect(output).toContain('done');
    expect(output).toContain('running');
  });
});

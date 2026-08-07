import { describe, it, expect } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { BenchmarkView } from '../../src/components/views/BenchmarkView.js';

describe('BenchmarkView Component Phase 5', () => {
  it('renders benchmark evaluation header, KPI metrics, and task table', () => {
    const tasks = [
      {
        taskId: 'TB-01',
        repo: 'django/django',
        issueTitle: 'Fix pagination offset in QuerySet.iterator()',
        status: 'passed' as const,
        durationSeconds: 42,
        cost: 0.14,
        tokens: 42110,
        harnessDeltaPass: '+23.6%'
      }
    ];

    const { lastFrame } = render(
      <BenchmarkView
        suiteName="Terminal-Bench Suite"
        tasks={tasks}
        overallPassRate={85.7}
        baselinePassRate={62.1}
        totalCost={1.42}
      />
    );

    const output = (lastFrame() || '').replace(/\s+/g, ' ');
    expect(output).toContain('Benchmark Evaluation View');
    expect(output).toContain('Terminal-Bench Suite');
    expect(output).toContain('Submitted Harness Pass Rate:');
    expect(output).toContain('85.7%');
    expect(output).toContain('Baseline Pass Rate:');
    expect(output).toContain('62.1%');
    expect(output).toContain('Δ Harness Lift:');
    expect(output).toContain('+23.6%');
    expect(output).toContain('[TB-01]');
    expect(output).toContain('django');
    expect(output).toContain('passed');
  });
});

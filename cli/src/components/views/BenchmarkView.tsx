import React from 'react';
import { Box, Text } from 'ink';
import Spinner from 'ink-spinner';
import { formatCurrency, formatTokenCount } from '../../utils/formatters.js';
import { SYMBOLS } from '../../utils/ansi.js';

export interface BenchmarkTaskItem {
  taskId: string;
  repo: string;
  issueTitle: string;
  status: 'passed' | 'failed' | 'running' | 'pending';
  durationSeconds?: number;
  cost?: number;
  tokens?: number;
  harnessDeltaPass?: string;
}

interface BenchmarkViewProps {
  suiteName?: string;
  tasks?: BenchmarkTaskItem[];
  overallPassRate?: number;
  baselinePassRate?: number;
  totalCost?: number;
}

export const BenchmarkView: React.FC<BenchmarkViewProps> = ({
  suiteName = 'Terminal-Bench & SWE-bench Lite (Ablation Benchmark Suite)',
  tasks,
  overallPassRate = 85.7,
  baselinePassRate = 62.1,
  totalCost = 1.42
}) => {
  const defaultTasks: BenchmarkTaskItem[] = tasks && tasks.length > 0 ? tasks : [
    {
      taskId: 'TB-01',
      repo: 'django/django',
      issueTitle: 'Fix pagination offset in QuerySet.iterator()',
      status: 'passed',
      durationSeconds: 42,
      cost: 0.14,
      tokens: 42110,
      harnessDeltaPass: '+23.6%'
    },
    {
      taskId: 'TB-02',
      repo: 'pytest-dev/pytest',
      issueTitle: 'Resolve fixture scope invalidation on parallel runs',
      status: 'passed',
      durationSeconds: 58,
      cost: 0.18,
      tokens: 53200,
      harnessDeltaPass: '+23.6%'
    },
    {
      taskId: 'TB-03',
      repo: 'scikit-learn/scikit-learn',
      issueTitle: 'Correct memory leak in Cython array slice',
      status: 'running',
      durationSeconds: 31,
      cost: 0.09,
      tokens: 28400,
      harnessDeltaPass: 'evaluating...'
    },
    {
      taskId: 'TB-04',
      repo: 'psf/requests',
      issueTitle: 'Handle chunked streaming socket timeout retry',
      status: 'pending'
    },
    {
      taskId: 'TB-05',
      repo: 'pallets/flask',
      issueTitle: 'Fix blueprint template folder resolution precedence',
      status: 'failed',
      durationSeconds: 65,
      cost: 0.21,
      tokens: 61000,
      harnessDeltaPass: '0%'
    }
  ];

  const delta = (overallPassRate - baselinePassRate).toFixed(1);

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      {/* Header Banner */}
      <Text color="cyan" bold>
        Benchmark Evaluation View — {suiteName}
      </Text>

      {/* Summary KPI Strip */}
      <Box marginY={1} paddingX={1} borderStyle="single" borderColor="magenta" justifyContent="space-between">
        <Text color="gray">
          Submitted Harness Pass Rate: <Text color="green" bold>{overallPassRate}%</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          Baseline Pass Rate: <Text color="yellow" bold>{baselinePassRate}%</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          Δ Harness Lift: <Text color="cyan" bold>+{delta}%</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          Batch Cost: <Text color="green" bold>{formatCurrency(totalCost)}</Text>
        </Text>
      </Box>

      {/* Multi-Task Batch Execution Table */}
      <Box flexDirection="column" marginY={1}>
        <Box borderStyle="single" borderColor="blue" paddingX={1} justifyContent="space-between">
          <Text color="cyan" bold>TASK ID / REPO</Text>
          <Text color="cyan" bold>ISSUE SUMMARY</Text>
          <Text color="cyan" bold>STATUS</Text>
          <Text color="cyan" bold>COST / LIFT</Text>
        </Box>

        {defaultTasks.map((t) => (
          <Box key={t.taskId} paddingX={1} justifyContent="space-between">
            <Box width="25%">
              <Text color="white" bold>[{t.taskId}] </Text>
              <Text color="gray">{t.repo.split('/')[1] || t.repo}</Text>
            </Box>

            <Box width="45%">
              <Text color="white">{t.issueTitle.length > 40 ? t.issueTitle.slice(0, 37) + '...' : t.issueTitle}</Text>
            </Box>

            <Box width="15%">
              {t.status === 'passed' ? (
                <Text color="green">{SYMBOLS.DONE} passed</Text>
              ) : t.status === 'running' ? (
                <Text color="yellow">
                  <Spinner type="dots" /> running
                </Text>
              ) : t.status === 'failed' ? (
                <Text color="red">{SYMBOLS.FAILED} failed</Text>
              ) : (
                <Text color="gray">{SYMBOLS.PENDING} pending</Text>
              )}
            </Box>

            <Box width="15%" justifyContent="flex-end">
              <Text color="green">{t.cost ? formatCurrency(t.cost) : '-'}</Text>
              <Text color="gray"> ({t.harnessDeltaPass || '-'})</Text>
            </Box>
          </Box>
        ))}
      </Box>

      {/* Footer Hotkeys */}
      <Box marginTop={1} gap={3}>
        <Text color="gray">Tab: switch view</Text>
        <Text color="magenta">/plan: task graph</Text>
        <Text color="magenta">/summary: reviewer summary</Text>
      </Box>
    </Box>
  );
};

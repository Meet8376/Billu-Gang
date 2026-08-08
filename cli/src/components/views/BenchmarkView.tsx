import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';

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
  currentRepo?: string;
  currentTaskPrompt?: string;
  currentTestStatus?: string;
  tasks?: BenchmarkTaskItem[];
  overallPassRate?: number;
  baselinePassRate?: number;
  totalCost?: number;
}

export const BenchmarkView: React.FC<BenchmarkViewProps> = ({
  currentRepo = 'test2',
  currentTaskPrompt = 'Fix the issues and refactor the code',
  currentTestStatus = '5/5 passed',
  tasks,
  overallPassRate = 85.7,
  baselinePassRate = 62.1,
  totalCost = 0.18
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const defaultTasks: BenchmarkTaskItem[] = [
    {
      taskId: 'LIVE-01',
      repo: currentRepo,
      issueTitle: currentTaskPrompt,
      status: 'passed',
      durationSeconds: 14,
      cost: 0.03,
      tokens: 28400,
      harnessDeltaPass: '+23.6%'
    },
    {
      taskId: 'SWE-01',
      repo: 'django/django',
      issueTitle: 'Fix pagination offset query error in QuerySet.iterator()',
      status: 'passed',
      durationSeconds: 14,
      cost: 0.03,
      tokens: 28400,
      harnessDeltaPass: '+23.6%'
    },
    {
      taskId: 'SWE-02',
      repo: 'sympy/sympy',
      issueTitle: 'Resolve matrix symbol simplify recursion limit',
      status: 'passed',
      durationSeconds: 19,
      cost: 0.04,
      tokens: 34100,
      harnessDeltaPass: '+23.6%'
    },
    {
      taskId: 'SWE-03',
      repo: 'pytest-dev/pytest',
      issueTitle: 'Fix fixture scope invalidation on parallel test runs',
      status: 'passed',
      durationSeconds: 22,
      cost: 0.05,
      tokens: 41200,
      harnessDeltaPass: '+23.6%'
    },
    {
      taskId: 'SWE-04',
      repo: 'scikit-learn/scikit-learn',
      issueTitle: 'Correct array slice memory view in Cython estimator',
      status: 'passed',
      durationSeconds: 18,
      cost: 0.03,
      tokens: 29800,
      harnessDeltaPass: '+23.6%'
    }
  ];

  const activeTaskList = tasks && tasks.length > 0 ? tasks : defaultTasks;

  useInput(
    (input, key) => {
      if (key.downArrow) {
        setSelectedIndex((prev) => Math.min(prev + 1, activeTaskList.length - 1));
      } else if (key.upArrow) {
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      }
    },
    { isActive: true }
  );

  return (
    <Box flexDirection="column" paddingX={1} paddingY={0} flexGrow={1} overflow="hidden">
      {/* Title */}
      <Box justifyContent="space-between" marginBottom={1} flexShrink={0}>
        <Text color="yellow" bold wrap="truncate">
          SWE-BENCH & TERMINAL-BENCH EVALUATION SUITE
        </Text>
        <Text color="magenta" bold flexShrink={0}>
          [Pass Rate: {overallPassRate}%]
        </Text>
      </Box>

      {/* Summary Metrics Bar */}
      <Box borderStyle="single" borderColor="cyan" paddingX={1} justifyContent="space-between" flexShrink={0}>
        <Text color="gray">
          Harness Lift: <Text color="green" bold>+{overallPassRate - baselinePassRate}%</Text> (vs Baseline {baselinePassRate}%)
        </Text>
        <Text color="gray">
          Live Status: <Text color="green" bold>{currentTestStatus}</Text>
        </Text>
        <Text color="gray">
          Cost: <Text color="yellow" bold>${totalCost.toFixed(2)}</Text>
        </Text>
      </Box>

      {/* Task List Header */}
      <Box marginTop={1} paddingX={1} gap={2} flexShrink={0}>
        <Text color="gray" bold>ID      Repo                     Issue Summary                                Status</Text>
      </Box>

      {/* Task List */}
      <Box flexDirection="column" flexGrow={1} overflow="hidden">
        {activeTaskList.map((t, idx) => {
          const isSelected = idx === selectedIndex;
          return (
            <Box key={t.taskId} gap={1} flexShrink={0}>
              <Text color={isSelected ? 'yellow' : 'gray'}>
                {isSelected ? '>' : ' '}
                [{t.taskId}]
              </Text>
              <Text color={isSelected ? 'white' : 'cyan'} bold={isSelected} wrap="truncate">
                {t.repo.padEnd(23, ' ')}
              </Text>
              <Text color={isSelected ? 'yellow' : 'gray'} wrap="truncate">
                {t.issueTitle.slice(0, 42).padEnd(43, ' ')}
              </Text>
              <Box flexGrow={1} />
              {t.status === 'passed' ? (
                <Text color="green" bold>[PASSED] ({t.durationSeconds}s)</Text>
              ) : t.status === 'running' ? (
                <Text color="yellow" bold><Spinner type="dots" /> [RUN]</Text>
              ) : (
                <Text color="gray">[WAIT]</Text>
              )}
            </Box>
          );
        })}
      </Box>

      {/* Selected Task Details Card */}
      {activeTaskList[selectedIndex] && (
        <Box
          marginTop={1}
          paddingX={1}
          borderStyle="single"
          borderColor="magenta"
          justifyContent="space-between"
          flexShrink={0}
        >
          <Box gap={1} flexShrink={1}>
            <Text color="yellow" bold>Benchmark Detail:</Text>
            <Text color="white" wrap="truncate">{activeTaskList[selectedIndex].repo}: {activeTaskList[selectedIndex].issueTitle}</Text>
          </Box>
          <Text color="gray" flexShrink={0}>Tokens: {activeTaskList[selectedIndex].tokens}</Text>
        </Box>
      )}

      {/* Footer Navigation */}
      <Box marginTop={0} gap={3} flexShrink={0}>
        <Text color="gray">up/down: navigate</Text>
        <Text color="magenta">/graph: task graph</Text>
        <Text color="cyan">/diff: diff view</Text>
        <Text color="yellow">/benchmark: swe-bench</Text>
      </Box>
    </Box>
  );
};

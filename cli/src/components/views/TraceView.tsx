import React from 'react';
import { Box, Text } from 'ink';
import Spinner from 'ink-spinner';
import { VerificationItem } from '../../api/apiTypes.js';
import { SYMBOLS } from '../../utils/ansi.js';

interface TraceViewProps {
  verifications?: VerificationItem[];
  logs?: string[];
  recoveringReason?: string;
  isVerificationRunning?: boolean;
}

export const TraceView: React.FC<TraceViewProps> = ({
  verifications,
  logs,
  recoveringReason,
  isVerificationRunning = false
}) => {
  const defaultSuites: VerificationItem[] = verifications && verifications.length > 0 ? verifications : [
    { name: 'build', status: 'passed', durationSeconds: 3.2 },
    { name: 'lint', status: 'passed', durationSeconds: 0.8 },
    { name: 'type check', status: 'passed', durationSeconds: 1.1 },
    { name: 'unit tests (312)', status: 'passed', durationSeconds: 11.4 },
    {
      name: 'regression tests (18)',
      status: 'failed',
      durationSeconds: 4.7,
      errorReason: 'test_pagination_last_page AssertionError'
    }
  ];

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      <Box gap={1} marginBottom={1}>
        <Text color="cyan" bold>
          Running verification suite…
        </Text>
        {isVerificationRunning && (
          <Text color="yellow">
            <Spinner type="dots" />
          </Text>
        )}
      </Box>

      <Box flexDirection="column" marginY={1}>
        {defaultSuites.map((item, idx) => (
          <Box key={idx} flexDirection="column">
            <Box gap={1}>
              <Text color="white">  {item.name}</Text>
              <Text color="gray">.............................</Text>
              {item.status === 'passed' ? (
                <Text color="green">
                  {SYMBOLS.DONE} passed ({item.durationSeconds}s)
                </Text>
              ) : item.status === 'running' ? (
                <Text color="yellow">
                  <Spinner type="dots" /> running...
                </Text>
              ) : item.status === 'failed' ? (
                <Text color="red">
                  {SYMBOLS.FAILED} 1 failed ({item.durationSeconds}s)
                </Text>
              ) : (
                <Text color="gray">{SYMBOLS.PENDING} pending</Text>
              )}
            </Box>
            {item.errorReason && (
              <Box marginX={4}>
                <Text color="red">└─ {item.errorReason}</Text>
              </Box>
            )}
          </Box>
        ))}
      </Box>

      {recoveringReason ? (
        <Box marginTop={1} padding={1} borderStyle="single" borderColor="yellow" flexDirection="column">
          <Text color="yellow" bold>
            Recovering: {recoveringReason}
          </Text>
          <Text color="gray" dimColor>
            Re-inspecting failing test → drafting patch → re-running verification suite
          </Text>
        </Box>
      ) : (
        <Box marginTop={1} paddingX={1} borderStyle="single" borderColor="gray">
          <Text color="gray">Status: </Text>
          <Text color="green">All automated verification gates active.</Text>
        </Box>
      )}

      {logs && logs.length > 0 && (
        <Box marginTop={1} flexDirection="column" borderStyle="single" borderColor="gray" paddingX={1}>
          <Text color="gray" bold>
            Live Execution Log Stream (last {Math.min(logs.length, 5)} events):
          </Text>
          {logs.slice(-5).map((logLine, i) => (
            <Text key={i} color="gray" dimColor>
              {logLine}
            </Text>
          ))}
        </Box>
      )}

      <Box marginTop={1} gap={3}>
        <Text color="gray">Tab: switch view</Text>
        <Text color="magenta">/plan: task graph</Text>
        <Text color="magenta">/summary: reviewer summary</Text>
      </Box>
    </Box>
  );
};

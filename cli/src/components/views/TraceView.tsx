import React from 'react';
import { Box, Text } from 'ink';
import { VerificationItem } from '../../api/apiTypes.js';
import { SYMBOLS } from '../../utils/ansi.js';

interface TraceViewProps {
  verifications?: VerificationItem[];
  logs?: string[];
  recoveringReason?: string;
}

export const TraceView: React.FC<TraceViewProps> = ({
  verifications,
  logs,
  recoveringReason
}) => {
  const defaultSuites: VerificationItem[] = verifications || [
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
      <Text color="cyan" bold>
        Running verification suite...
      </Text>
      <Box flexDirection="column" marginY={1}>
        {defaultSuites.map((item, idx) => (
          <Box key={idx} flexDirection="column">
            <Box gap={1}>
              <Text color="white">  {item.name}</Text>
              <Text color="gray">.............................</Text>
              <Text color={item.status === 'passed' ? 'green' : 'red'}>
                {item.status === 'passed' ? SYMBOLS.DONE : SYMBOLS.FAILED}{' '}
                {item.status} ({item.durationSeconds}s)
              </Text>
            </Box>
            {item.errorReason && (
              <Box marginX={4}>
                <Text color="red">└─ {item.errorReason}</Text>
              </Box>
            )}
          </Box>
        ))}
      </Box>

      {recoveringReason && (
        <Box marginTop={1} padding={1} borderStyle="single" borderColor="yellow">
          <Text color="yellow" bold>
            Recovering: {recoveringReason}
          </Text>
        </Box>
      )}

      {logs && logs.length > 0 && (
        <Box marginTop={1} flexDirection="column">
          <Text color="gray" bold>
            Execution Logs:
          </Text>
          {logs.slice(-5).map((log, i) => (
            <Text key={i} color="gray" dimColor>
              {log}
            </Text>
          ))}
        </Box>
      )}
    </Box>
  );
};

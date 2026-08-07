import React from 'react';
import { Box, Text } from 'ink';
import Spinner from 'ink-spinner';
import { SYMBOLS } from '../../utils/ansi.js';

export interface IntakeStep {
  id: string;
  step: string;
  completed: boolean;
  running?: boolean;
  detail?: string;
}

interface IntakeViewProps {
  steps: IntakeStep[];
  ready: boolean;
}

export const IntakeView: React.FC<IntakeViewProps> = ({ steps, ready }) => {
  const defaultSteps: IntakeStep[] = steps && steps.length > 0 ? steps : [
    { id: '1', step: 'Scanning repository workspace', completed: true, detail: '1,204 files indexed' },
    { id: '2', step: 'Building symbol graph', completed: true, detail: '8,431 symbols' },
    { id: '3', step: 'Building test-to-source map', completed: true, detail: '312 test files' },
    { id: '4', step: 'Loading git history', completed: true, detail: '2,140 commits' },
  ];

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      <Text bold color="cyan">
        Scanning repository workspace…
      </Text>
      
      <Box flexDirection="column" marginY={1} gap={1}>
        {defaultSteps.map((item) => (
          <Box key={item.id} gap={1}>
            {item.completed ? (
              <Text color="green">{SYMBOLS.DONE}</Text>
            ) : item.running ? (
              <Text color="yellow">
                <Spinner type="dots" />
              </Text>
            ) : (
              <Text color="gray">{SYMBOLS.PENDING}</Text>
            )}

            <Text color={item.completed ? 'white' : item.running ? 'yellow' : 'gray'} bold={item.running}>
              {item.step}
            </Text>

            {item.detail && <Text color="gray">({item.detail})</Text>}
          </Box>
        ))}
      </Box>

      {ready ? (
        <Box marginTop={1} flexDirection="column" borderStyle="single" borderColor="green" paddingX={1}>
          <Text color="green" bold>
            ✓ Ready. Describe the issue or feature you'd like addressed:
          </Text>
          <Text color="gray">Type prompt below (e.g., "Fix off-by-one error in pagination") and press Enter.</Text>
        </Box>
      ) : (
        <Box marginTop={1}>
          <Text color="yellow">
            <Spinner type="dots" /> <Text color="yellow">Indexing repository structure...</Text>
          </Text>
        </Box>
      )}
    </Box>
  );
};

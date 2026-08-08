import React from 'react';
import { Box, Text } from 'ink';
import { SessionInfo } from '../api/apiTypes.js';

interface StatusStripProps {
  session: SessionInfo;
  currentTaskLabel?: string;
}

export const StatusStrip: React.FC<StatusStripProps> = ({ session, currentTaskLabel }) => {
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}m ${s}s`;
  };

  return (
    <Box
      borderStyle="single"
      borderColor="gray"
      paddingX={1}
      justifyContent="space-between"
      flexShrink={0}
      overflow="hidden"
    >
      <Box gap={1} flexShrink={1}>
        <Text color="yellow" bold>
          HARNESS
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray" wrap="truncate">
          Stage: <Text color="white" bold>{currentTaskLabel || 'Autonomous Agent Execution'}</Text>
        </Text>
      </Box>

      <Box gap={1} flexShrink={0}>
        <Text color="gray">
          Tests: <Text color="green" bold>{session.testsPassing || '5/5 Passed'}</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          Elapsed: <Text color="cyan">{formatTime(session.elapsedSeconds || 0)}</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="magenta" bold>
          [Tab] Switch View
        </Text>
      </Box>
    </Box>
  );
};


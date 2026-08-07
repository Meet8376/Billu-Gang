import React from 'react';
import { Box, Text } from 'ink';
import { SessionInfo } from '../api/apiTypes.js';
import { formatElapsedTime } from '../utils/formatters.js';

interface HeaderBarProps {
  session: SessionInfo;
  activeView: string;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ session, activeView }) => {
  return (
    <Box
      borderStyle="single"
      borderColor="blue"
      paddingX={1}
      justifyContent="space-between"
    >
      <Box gap={1}>
        <Text color="blue" bold>
          AE-01 HARNESS
        </Text>
        <Text color="gray">|</Text>
        <Text color="cyan" bold>
          {session.repoName}
        </Text>
        <Text color="gray">({session.branch})</Text>
      </Box>

      <Box gap={2}>
        <Text color="magenta">Model: {session.modelProvider}</Text>
        <Text color="gray">|</Text>
        <Text color="yellow">ID: {session.sessionId}</Text>
        <Text color="gray">|</Text>
        <Text color="green">Time: {formatElapsedTime(session.elapsedSeconds)}</Text>
        <Text color="gray">|</Text>
        <Text color="white" bold>
          VIEW: [{activeView.toUpperCase()}]
        </Text>
      </Box>
    </Box>
  );
};

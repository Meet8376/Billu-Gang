import React from 'react';
import { Box, Text } from 'ink';
import { SessionInfo } from '../api/apiTypes.js';

interface HeaderBarProps {
  session: SessionInfo;
  activeView: string;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ session }) => {
  return (
    <Box flexDirection="column" borderStyle="double" borderColor="cyan" paddingX={1} marginY={0}>
      <Text color="cyan" bold>
        =========================================================
      </Text>
      <Text color="blue" bold>
        Secure AI Code Review Sandbox
      </Text>
      <Text color="cyan" bold>
        =========================================================
      </Text>
      <Box flexDirection="column" marginY={0}>
        <Box gap={2}>
          <Text color="gray">Repository :</Text>
          <Text color="white" bold>{session.repoName}</Text>
        </Box>
        <Box gap={2}>
          <Text color="gray">Branch     :</Text>
          <Text color="yellow">{session.branch || 'main'}</Text>
        </Box>
        <Box gap={2}>
          <Text color="gray">AI Model   :</Text>
          <Text color="magenta" bold>{session.modelProvider}</Text>
        </Box>
        <Box gap={2}>
          <Text color="gray">Status     :</Text>
          <Text color="green" bold>[{session.sandboxState?.toUpperCase() || 'RUNNING'}]</Text>
        </Box>
      </Box>
    </Box>
  );
};

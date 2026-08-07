import React from 'react';
import { Box, Text } from 'ink';
import { SessionInfo } from '../api/apiTypes.js';

interface StatusStripProps {
  session: SessionInfo;
  currentTaskLabel?: string;
}

export const StatusStrip: React.FC<StatusStripProps> = ({ session, currentTaskLabel }) => {
  return (
    <Box
      borderStyle="single"
      borderColor="gray"
      paddingX={1}
      justifyContent="space-between"
    >
      <Box gap={1}>
        <Text color="gray">Sandbox Status:</Text>
        <Text color="green" bold>
          [{session.sandboxState?.toUpperCase() || 'ACTIVE'}]
        </Text>
        {currentTaskLabel && (
          <>
            <Text color="gray">|</Text>
            <Text color="white">Stage: {currentTaskLabel}</Text>
          </>
        )}
      </Box>

      <Box gap={2}>
        <Text color="gray">
          Tests: <Text color="cyan" bold>{session.testsPassing || 'All Passed'}</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="magenta">Tab: Switch View</Text>
      </Box>
    </Box>
  );
};

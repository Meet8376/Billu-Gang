import React from 'react';
import { Box, Text } from 'ink';
import { SessionInfo } from '../api/apiTypes.js';
import { formatCurrency, formatTokenCount } from '../utils/formatters.js';

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
        <Text color="gray">Status:</Text>
        <Text color={session.sandboxState === 'sandboxed' ? 'green' : 'yellow'}>
          [{session.sandboxState.toUpperCase()}]
        </Text>
        {currentTaskLabel && (
          <>
            <Text color="gray">|</Text>
            <Text color="white">Active: {currentTaskLabel}</Text>
          </>
        )}
      </Box>

      <Box gap={2}>
        <Text color="gray">
          Tokens: <Text color="white">{formatTokenCount(session.tokensUsed)}</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          Cost: <Text color="green">{formatCurrency(session.costSoFar)}</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          Tests: <Text color="cyan">{session.testsPassing}</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="magenta">Tab: Switch View</Text>
      </Box>
    </Box>
  );
};

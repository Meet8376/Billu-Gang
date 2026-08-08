import React from 'react';
import { Box, Text } from 'ink';
import { SessionInfo } from '../api/apiTypes.js';

interface HeaderBarProps {
  session: SessionInfo;
  activeView: string;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ session, activeView }) => {
  return (
    <Box
      flexDirection="column"
      borderStyle="round"
      borderColor="yellow"
      paddingX={1}
      marginY={0}
      flexShrink={0}
    >
      {/* Title Bar */}
      <Box justifyContent="space-between" alignItems="center">
        <Text color="yellow" bold>
          BILLU GANG  |  AGENTIC HARNESS
        </Text>
        <Text color="magenta" bold>
          [{session.modelProvider || 'gemini-3.5-flash-lite'}]
        </Text>

      </Box>

      {/* Info Row */}
      <Box gap={1} marginTop={0} flexWrap="wrap">
        <Text color="gray">
          Repo: <Text color="white" bold>{session.repoName}</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          Tier: {session.tier === 'algo' ? (
            (session.algoBalance ?? 0) > 0 ? (
              <Text color="yellow" bold>[ALGO: {session.algoBalance} ALGO (${(session.algoBalance * 0.2).toFixed(2)})]</Text>
            ) : (
              <Text color="red" bold>[ALGO: UNPAID (0.0 ALGO)]</Text>
            )
          ) : (
            <Text color="cyan" bold>[FREE TIER]</Text>
          )}
        </Text>

        <Text color="gray">|</Text>
        <Text color="gray">
          Branch: <Text color="cyan">{session.branch || 'main'}</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          Sandbox: <Text color="green" bold>[{session.sandboxState?.toUpperCase() || 'ACTIVE'}]</Text>
        </Text>
        <Text color="gray">|</Text>
        <Text color="gray">
          View: <Text color="yellow" bold>{activeView === 'graph' ? 'Task Graph' : activeView === 'diff' ? 'Diff View' : 'SWE Benchmark'}</Text>
        </Text>
      </Box>
    </Box>
  );
};



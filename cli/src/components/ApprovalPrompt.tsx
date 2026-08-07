import React from 'react';
import { Box, Text, useInput } from 'ink';

export interface PendingApprovalRequest {
  id: string;
  command: string;
  reason: string;
  requestedAt: string;
}

interface ApprovalPromptProps {
  request?: PendingApprovalRequest;
  commandToApprove?: string;
  reason?: string;
  onRespond: (approved: boolean) => void;
}

export const ApprovalPrompt: React.FC<ApprovalPromptProps> = ({
  request,
  commandToApprove,
  reason,
  onRespond
}) => {
  const targetCommand = request ? request.command : commandToApprove || 'npm install package-outside-scope';
  const targetReason = request ? request.reason : reason || 'Accesses network outside sandbox allowlist';

  useInput((input, key) => {
    if (input.toLowerCase() === 'y') {
      onRespond(true);
    } else if (input.toLowerCase() === 'n' || key.escape || key.return) {
      onRespond(false);
    }
  }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });

  return (
    <Box
      flexDirection="column"
      borderStyle="double"
      borderColor="red"
      padding={1}
      margin={1}
    >
      <Text color="red" bold>
        ⚠️ SAFETY APPROVAL REQUIRED — OUT-OF-SCOPE COMMAND
      </Text>
      
      <Box marginY={1}>
        <Text color="yellow">Reason: </Text>
        <Text color="white">{targetReason}</Text>
      </Box>

      <Box marginY={1} paddingX={1} borderStyle="single" borderColor="yellow" flexDirection="column">
        <Text color="gray">Proposed Command:</Text>
        <Text color="white" bold>
          {targetCommand}
        </Text>
      </Box>

      <Box marginTop={1} gap={1}>
        <Text color="white">
          Allow harness to execute this command in sandbox? [
        </Text>
        <Text color="green" bold underline>
          y
        </Text>
        <Text color="white">/</Text>
        <Text color="red" bold underline>
          N
        </Text>
        <Text color="white">]:</Text>
      </Box>

      <Box marginTop={1}>
        <Text color="gray" dimColor>
          Press 'y' to approve, or 'n' / Esc to block execution (Default: Deny).
        </Text>
      </Box>
    </Box>
  );
};

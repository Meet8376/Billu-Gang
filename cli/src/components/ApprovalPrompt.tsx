import React from 'react';
import { Box, Text, useInput } from 'ink';

export interface PendingApprovalRequest {
  id?: string;
  command?: string;
  reason?: string;
  repoName?: string;
  branch?: string;
  requestedAt?: string;
}

interface ApprovalPromptProps {
  request?: PendingApprovalRequest;
  commandToApprove?: string;
  reason?: string;
  repoName?: string;
  branch?: string;
  onRespond: (approved: boolean) => void;
}

export const ApprovalPrompt: React.FC<ApprovalPromptProps> = ({
  request,
  commandToApprove,
  reason,
  repoName,
  branch,
  onRespond
}) => {
  const targetCommand = request?.command || commandToApprove || 'git push origin main';
  const targetReason = request?.reason || reason || 'Pushing verified commits & code patches to remote GitHub repository';
  const targetRepo = request?.repoName || repoName || 'Billu-Gang';
  const targetBranch = request?.branch || branch || 'main';

  useInput(
    (input, key) => {
      if (input.toLowerCase() === 'y') {
        onRespond(true);
      } else if (input.toLowerCase() === 'n' || key.escape || key.return) {
        onRespond(false);
      }
    },
    { isActive: Boolean(process.stdin && process.stdin.isTTY) }
  );

  return (
    <Box
      flexDirection="column"
      borderStyle="round"
      borderColor="yellow"
      paddingX={2}
      paddingY={1}
      margin={1}
    >
      {/* Crown Banner */}
      <Box justifyContent="center" marginBottom={1}>
        <Text color="yellow" bold>
          👑 ROYAL HARNESS — GITHUB CODE PUSH APPROVAL
        </Text>
      </Box>

      {/* Target Details */}
      <Box flexDirection="column" borderStyle="single" borderColor="magenta" paddingX={1} marginY={1}>
        <Box gap={2}>
          <Text color="yellow" bold>Repository :</Text>
          <Text color="white" bold>{targetRepo}</Text>
        </Box>
        <Box gap={2}>
          <Text color="yellow" bold>Branch     :</Text>
          <Text color="cyan">{targetBranch}</Text>
        </Box>
        <Box gap={2}>
          <Text color="yellow" bold>Command    :</Text>
          <Text color="green" bold>{targetCommand}</Text>
        </Box>
        <Box gap={2}>
          <Text color="yellow" bold>Reason     :</Text>
          <Text color="white">{targetReason}</Text>
        </Box>
      </Box>

      {/* Safety Notice */}
      <Box marginY={1}>
        <Text color="yellow" bold>
          🛡️  SECURITY NOTICE:
        </Text>
        <Text color="gray">
          {' '}This action will write local codebase modifications directly to GitHub.
        </Text>
      </Box>

      {/* Action Prompt */}
      <Box marginTop={1} gap={1} alignItems="center">
        <Text color="white" bold>
          Push code to GitHub? [
        </Text>
        <Text color="green" bold underline>
          y
        </Text>
        <Text color="white">/</Text>
        <Text color="red" bold underline>
          N
        </Text>
        <Text color="white" bold>
          ]:
        </Text>
      </Box>

      <Box marginTop={1}>
        <Text color="gray" dimColor>
          Press 'y' to confirm & push to GitHub | Press 'n' or Esc to cancel execution (Default: Deny)
        </Text>
      </Box>
    </Box>
  );
};

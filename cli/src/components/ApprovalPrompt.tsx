import React from 'react';
import { Box, Text, useInput } from 'ink';

interface ApprovalPromptProps {
  commandToApprove: string;
  reason: string;
  onRespond: (approved: boolean) => void;
}

export const ApprovalPrompt: React.FC<ApprovalPromptProps> = ({
  commandToApprove,
  reason,
  onRespond
}) => {
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
        ⚠️ SAFETY APPROVAL REQUIRED
      </Text>
      <Text color="yellow">Reason: {reason}</Text>
      <Box marginY={1} paddingX={1} borderStyle="single" borderColor="yellow">
        <Text color="white" bold>
          {commandToApprove}
        </Text>
      </Box>
      <Text color="white">
        Allow harness to execute this command in sandbox? [<Text color="green" bold>y</Text>/
        <Text color="red" bold>N</Text>]:
      </Text>
    </Box>
  );
};

import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

interface CommandLineProps {
  onSubmit: (command: string) => void;
  disabled?: boolean;
}

export const CommandLine: React.FC<CommandLineProps> = ({ onSubmit, disabled = false }) => {
  const [input, setInput] = useState('');

  useInput(
    (char, key) => {
      if (disabled) return;

      if (key.return) {
        if (input.trim().length > 0) {
          onSubmit(input.trim());
          setInput('');
        }
      } else if (key.backspace || key.delete) {
        setInput((prev) => prev.slice(0, -1));
      } else if (char && !key.ctrl && !key.meta) {
        setInput((prev) => prev + char);
      }
    },
    { isActive: true }
  );

  return (
    <Box paddingX={1} borderStyle="round" borderColor="magenta">
      <Text color="yellow" bold>
        👑 ROYAL PROMPT &gt;{' '}
      </Text>
      <Text color="white" bold>
        {input}
      </Text>
      <Text color="yellow" dimColor>
        _
      </Text>
    </Box>
  );
};

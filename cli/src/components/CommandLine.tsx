import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

interface CommandLineProps {
  onSubmit: (command: string) => void;
  disabled?: boolean;
}

export const CommandLine: React.FC<CommandLineProps> = ({ onSubmit, disabled = false }) => {
  const [input, setInput] = useState('');

  useInput((char, key) => {
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
  }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });

  return (
    <Box paddingX={1} borderStyle="single" borderColor="magenta">
      <Text color="magenta" bold>
        &gt;{' '}
      </Text>
      <Text color="white">{input}</Text>
      <Text color="magenta" dimColor>
        _
      </Text>
    </Box>
  );
};

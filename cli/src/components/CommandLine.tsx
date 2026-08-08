import React, { useState } from 'react';
import { Box, Text, useInput, useStdout } from 'ink';

interface CommandLineProps {
  onSubmit: (command: string) => void;
  disabled?: boolean;
}

export const CommandLine: React.FC<CommandLineProps> = ({ onSubmit, disabled = false }) => {
  const [input, setInput] = useState('');
  const { stdout } = useStdout();

  const columns = stdout?.columns || process.stdout.columns || 80;
  // Prompt prefix "PROMPT > " is 9 chars, borders padding 4 chars -> max input display len
  const maxInputLen = Math.max(10, columns - 15);

  const displayInput = input.length > maxInputLen
    ? '...' + input.slice(input.length - maxInputLen + 3)
    : input;

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
    <Box paddingX={1} borderStyle="round" borderColor="magenta" flexShrink={0} overflow="hidden">
      <Text color="yellow" bold>
        PROMPT &gt;{' '}
      </Text>
      <Text color="white" bold wrap="truncate">
        {displayInput}
      </Text>
      <Text color="yellow" dimColor>
        _
      </Text>
    </Box>
  );
};


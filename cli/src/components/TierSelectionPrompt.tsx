import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

interface TierSelectionPromptProps {
  onSelectTier: (tier: 'free' | 'algo') => void;
}

export const TierSelectionPrompt: React.FC<TierSelectionPromptProps> = ({ onSelectTier }) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const options = [
    {
      id: 'free',
      label: '[1] FREE TIER — Bring Your Own API Key',
      detail: 'Free access using your own Gemini / OpenAI / Anthropic API keys.'
    },
    {
      id: 'algo',
      label: '[2] ALGORAND PAID TIER — Pay-As-You-Go via ALGO Blockchain',
      detail: 'Pay-per-use using ALGO tokens on Algorand testnet/mainnet with real-time balance tracking.'
    }
  ];

  useInput(
    (input, key) => {
      if (key.downArrow) {
        setSelectedIndex((prev) => Math.min(prev + 1, options.length - 1));
      } else if (key.upArrow) {
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      } else if (key.return) {
        onSelectTier(options[selectedIndex].id as 'free' | 'algo');
      } else if (input === '1') {
        onSelectTier('free');
      } else if (input === '2') {
        onSelectTier('algo');
      }
    },
    { isActive: true }
  );

  return (
    <Box
      flexDirection="column"
      borderStyle="round"
      borderColor="cyan"
      paddingX={2}
      paddingY={1}
      width={78}
    >
      <Box justifyContent="center" marginBottom={1}>
        <Text color="yellow" bold>
          BILLU GANG AGENTIC HARNESS — SELECT ACCESS TIER
        </Text>
      </Box>

      <Box flexDirection="column" gap={1} marginBottom={1}>
        {options.map((opt, idx) => {
          const isSelected = idx === selectedIndex;
          return (
            <Box key={opt.id} flexDirection="column">
              <Text color={isSelected ? 'yellow' : 'white'} bold={isSelected}>
                {isSelected ? '> ' : '  '}
                {opt.label}
              </Text>
              <Box paddingLeft={4}>
                <Text color="gray">{opt.detail}</Text>
              </Box>
            </Box>
          );
        })}
      </Box>

      <Box borderStyle="single" borderColor="gray" paddingX={1} marginTop={1}>
        <Text color="gray">
          Press <Text color="yellow" bold>1</Text> or <Text color="yellow" bold>2</Text>, use <Text color="cyan" bold>up/down arrows</Text>, and hit <Text color="green" bold>Enter</Text> to confirm.
        </Text>
      </Box>
    </Box>
  );
};

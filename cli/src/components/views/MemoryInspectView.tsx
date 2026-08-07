import React from 'react';
import { Box, Text } from 'ink';
import { MemoryItem } from '../../api/apiTypes.js';

interface MemoryInspectViewProps {
  memoryItems?: MemoryItem[];
}

export const MemoryInspectView: React.FC<MemoryInspectViewProps> = ({ memoryItems }) => {
  const defaultItems: MemoryItem[] = memoryItems || [
    {
      id: 'mem-01',
      tier: 'working',
      content: 'Paginator start index adjusted to (page - 1) * size',
      provenance: 'AST indexer + code edit step 3a',
      invalidationRule: 'Invalidate on paginator.py change',
      createdAt: '2026-08-07 12:45:00'
    },
    {
      id: 'mem-02',
      tier: 'project',
      content: 'Pytest configuration targets tests/ directory',
      provenance: 'repo_scanner: pytest.ini',
      createdAt: '2026-08-07 12:40:00'
    }
  ];

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      <Text color="cyan" bold>
        Tiered Memory Inspection Browser (7 Tiers)
      </Text>
      <Box flexDirection="column" marginY={1}>
        {defaultItems.map((item) => (
          <Box key={item.id} flexDirection="column" borderStyle="single" borderColor="gray" paddingX={1} marginY={1}>
            <Box justifyContent="space-between">
              <Text color="magenta" bold>
                [{item.tier.toUpperCase()}] {item.id}
              </Text>
              <Text color="gray">{item.createdAt}</Text>
            </Box>
            <Text color="white">{item.content}</Text>
            <Text color="yellow">Provenance: {item.provenance}</Text>
            {item.invalidationRule && (
              <Text color="red" dimColor>
                Rule: {item.invalidationRule}
              </Text>
            )}
          </Box>
        ))}
      </Box>
    </Box>
  );
};

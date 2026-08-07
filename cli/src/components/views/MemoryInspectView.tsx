import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import { MemoryItem } from '../../api/apiTypes.js';

export type MemoryTierFilter = 'all' | 'working' | 'task' | 'project' | 'episodic' | 'procedural' | 'preference' | 'evidence';

interface MemoryInspectViewProps {
  memoryItems?: MemoryItem[];
  onDeleteItem?: (id: string) => void;
  onExportMemory?: () => void;
}

export const MemoryInspectView: React.FC<MemoryInspectViewProps> = ({
  memoryItems,
  onDeleteItem,
  onExportMemory
}) => {
  const defaultItems: MemoryItem[] = memoryItems && memoryItems.length > 0 ? memoryItems : [
    {
      id: 'mem-01',
      tier: 'working',
      content: 'Paginator start index adjusted to (page - 1) * size',
      provenance: 'AST Indexer + Edit Step 3a | Conf: 0.98',
      invalidationRule: 'Auto-expire on paginator.py file change',
      createdAt: '2026-08-07 12:45:00'
    },
    {
      id: 'mem-02',
      tier: 'task',
      content: 'Issue report: page calculation off by one on page >= 2',
      provenance: 'User Prompt Input | Conf: 1.00',
      createdAt: '2026-08-07 12:40:00'
    },
    {
      id: 'mem-03',
      tier: 'project',
      content: 'Pytest suite configuration targets tests/ directory',
      provenance: 'repo_scanner: pytest.ini | Conf: 1.00',
      createdAt: '2026-08-07 12:35:00'
    },
    {
      id: 'mem-04',
      tier: 'episodic',
      content: 'Previous run recovered from regression test failure by re-running paginator fixture',
      provenance: 'Episodic Memory Logger | Conf: 0.92',
      invalidationRule: 'Expire after 24h session window',
      createdAt: '2026-08-07 12:30:00'
    },
    {
      id: 'mem-05',
      tier: 'procedural',
      content: 'Procedure: Always run pytest -v tests/test_paginator.py after editing paginator.py',
      provenance: 'Procedural Rule Engine | Conf: 0.95',
      createdAt: '2026-08-07 12:20:00'
    },
    {
      id: 'mem-06',
      tier: 'preference',
      content: 'User prefers concise unified diff summaries over full file output',
      provenance: 'User CLI Settings | Conf: 1.00',
      createdAt: '2026-08-07 12:10:00'
    },
    {
      id: 'mem-07',
      tier: 'evidence',
      content: 'Verification evidence: 330/330 unit tests passed cleanly inside Docker sandbox',
      provenance: 'Verification Pipeline Run #4 | Conf: 1.00',
      createdAt: '2026-08-07 12:50:00'
    }
  ];

  const tiers: MemoryTierFilter[] = [
    'all',
    'working',
    'task',
    'project',
    'episodic',
    'procedural',
    'preference',
    'evidence'
  ];

  const [selectedTierIndex, setSelectedTierIndex] = useState<number>(0);
  const activeTier = tiers[selectedTierIndex];

  useInput((input, key) => {
    if (key.rightArrow) {
      setSelectedTierIndex((prev) => (prev + 1) % tiers.length);
    } else if (key.leftArrow) {
      setSelectedTierIndex((prev) => (prev - 1 + tiers.length) % tiers.length);
    } else if (input.toLowerCase() === 'e' && onExportMemory) {
      onExportMemory();
    }
  }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });

  const filteredItems = activeTier === 'all'
    ? defaultItems
    : defaultItems.filter((item) => item.tier === activeTier);

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      <Text color="cyan" bold>
        Tiered Memory Inspection Browser (7 Core Surfaces FR9–FR12)
      </Text>

      {/* Tier Filter Bar */}
      <Box gap={1} marginY={1}>
        <Text color="gray">Tiers: </Text>
        {tiers.map((t, idx) => (
          <Text
            key={t}
            color={idx === selectedTierIndex ? 'magenta' : 'gray'}
            bold={idx === selectedTierIndex}
            underline={idx === selectedTierIndex}
          >
            [{t.toUpperCase()}]
          </Text>
        ))}
      </Box>

      {/* Items List */}
      <Box flexDirection="column" marginY={1}>
        {filteredItems.length === 0 ? (
          <Text color="gray">No memory items found in tier [{activeTier.toUpperCase()}].</Text>
        ) : (
          filteredItems.map((item) => (
            <Box
              key={item.id}
              flexDirection="column"
              borderStyle="single"
              borderColor={idxColor(item.tier)}
              paddingX={1}
              marginY={1}
            >
              <Box justifyContent="space-between">
                <Text color={idxColor(item.tier)} bold>
                  [{item.tier.toUpperCase()}] {item.id}
                </Text>
                <Text color="gray">{item.createdAt}</Text>
              </Box>

              <Text color="white" bold>
                {item.content}
              </Text>

              <Box marginTop={1} gap={2}>
                <Text color="yellow">Provenance: {item.provenance}</Text>
              </Box>

              {item.invalidationRule && (
                <Text color="red" dimColor>
                  Rule: {item.invalidationRule}
                </Text>
              )}
            </Box>
          ))
        )}
      </Box>

      {/* Footer controls */}
      <Box marginTop={1} gap={3}>
        <Text color="gray">←/→: cycle memory tiers</Text>
        <Text color="magenta">e: export memory snapshot</Text>
        <Text color="magenta">/rollback: trigger rollback</Text>
      </Box>
    </Box>
  );
};

function idxColor(tier: string): string {
  switch (tier) {
    case 'working': return 'yellow';
    case 'task': return 'cyan';
    case 'project': return 'blue';
    case 'episodic': return 'magenta';
    case 'procedural': return 'green';
    case 'preference': return 'white';
    case 'evidence': return 'green';
    default: return 'gray';
  }
}

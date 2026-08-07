import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import { DiffPatch } from '../../api/apiTypes.js';

interface DiffViewProps {
  patches?: DiffPatch[];
  activeFileFilter?: string;
}

export const DiffView: React.FC<DiffViewProps> = ({ patches, activeFileFilter }) => {
  const defaultPatches: DiffPatch[] = patches && patches.length > 0 ? patches : [
    {
      filePath: 'paginator.py',
      additions: 4,
      deletions: 2,
      diffHunks: [
        '  42   def get_page(items, page, size):',
        '  43 -     start = page * size',
        '  44 -     end = start + size',
        '  43 +     start = (page - 1) * size',
        '  44 +     end = start + size',
        '  45       return items[start:end]'
      ]
    },
    {
      filePath: 'tests/test_paginator.py',
      additions: 8,
      deletions: 0,
      diffHunks: [
        '  105   def test_pagination_first_page():',
        '  106 +     res = get_page([1, 2, 3, 4], page=1, size=2)',
        '  107 +     assert res == [1, 2]',
        '  108 +',
        '  109 + def test_pagination_last_page():',
        '  110 +     res = get_page([1, 2, 3, 4], page=2, size=2)',
        '  111 +     assert res == [3, 4]'
      ]
    }
  ];

  const filteredPatches = activeFileFilter
    ? defaultPatches.filter((p) => p.filePath.toLowerCase().includes(activeFileFilter.toLowerCase()))
    : defaultPatches;

  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const currentPatch = filteredPatches[activeFileIndex] || defaultPatches[0];

  useInput((input, key) => {
    if (key.rightArrow) {
      setActiveFileIndex((prev) => (prev + 1) % filteredPatches.length);
    } else if (key.leftArrow) {
      setActiveFileIndex((prev) => (prev - 1 + filteredPatches.length) % filteredPatches.length);
    }
  }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      {/* File Selector Bar */}
      <Box gap={2} marginBottom={1}>
        {filteredPatches.map((p, idx) => (
          <Box key={p.filePath} gap={1}>
            <Text
              color={idx === activeFileIndex ? 'cyan' : 'gray'}
              bold={idx === activeFileIndex}
              underline={idx === activeFileIndex}
            >
              {p.filePath}
            </Text>
            <Text>
              <Text color="green">+{p.additions}</Text> <Text color="red">−{p.deletions}</Text>
            </Text>
          </Box>
        ))}
      </Box>

      {/* Header for current file */}
      <Box borderStyle="single" borderColor="blue" paddingX={1} justifyContent="space-between">
        <Text color="cyan" bold>
          {currentPatch.filePath}
        </Text>
        <Text>
          <Text color="green">+{currentPatch.additions}</Text>{' '}
          <Text color="red">−{currentPatch.deletions}</Text>
        </Text>
      </Box>

      {/* Diff Content */}
      <Box flexDirection="column" marginY={1}>
        {currentPatch.diffHunks.map((line, idx) => {
          if (line.includes(' + ')) {
            return (
              <Text key={idx} color="green">
                {line}
              </Text>
            );
          }
          if (line.includes(' - ')) {
            return (
              <Text key={idx} color="red" dimColor>
                {line}
              </Text>
            );
          }
          return (
            <Text key={idx} color="gray">
              {line}
            </Text>
          );
        })}
      </Box>

      <Box marginTop={1} gap={2}>
        <Text color="gray">←/→: switch file diff</Text>
        <Text color="magenta">/plan: task graph</Text>
        <Text color="magenta">/trace: trace logs</Text>
      </Box>
    </Box>
  );
};

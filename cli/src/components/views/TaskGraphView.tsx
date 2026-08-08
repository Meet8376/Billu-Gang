import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';
import { TaskGraphNode } from '../../api/apiTypes.js';

interface TaskGraphViewProps {
  taskTitle: string;
  nodes: TaskGraphNode[];
  maxVisibleNodes?: number;
  onSelectNode?: (node: TaskGraphNode) => void;
}

export const TaskGraphView: React.FC<TaskGraphViewProps> = ({
  taskTitle,
  nodes,
  maxVisibleNodes = 8,
  onSelectNode
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const defaultNodes: TaskGraphNode[] =
    nodes && nodes.length > 0
      ? nodes
      : [
          { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Source files indexed' },
          { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols & AST mapped' },
          { id: '3', label: 'Execute verification test suite', status: 'running', detail: 'Pytest harness active' },
          { id: '4', label: 'Gemini AI code review', status: 'pending', detail: 'Waiting for model artifacts' },
          { id: '5', label: 'Push verified patch to GitHub', status: 'pending', detail: 'git push origin main' }
        ];

  useInput(
    (input, key) => {
      if (key.downArrow) {
        setSelectedIndex((prev) => Math.min(prev + 1, defaultNodes.length - 1));
      } else if (key.upArrow) {
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      } else if (key.return && onSelectNode) {
        onSelectNode(defaultNodes[selectedIndex]);
      }
    },
    { isActive: true }
  );

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'done':
      case 'completed':
        return <Text color="green" bold>[DONE]</Text>;
      case 'running':
        return (
          <Text color="yellow" bold>
            <Spinner type="dots" /> [RUN]
          </Text>
        );
      case 'failed':
        return <Text color="red" bold>[FAIL]</Text>;
      default:
        return <Text color="gray">[WAIT]</Text>;
    }
  };

  // Slice nodes for height safety to prevent terminal scrolling & flickering
  const visibleNodes = defaultNodes.slice(0, maxVisibleNodes);

  return (
    <Box flexDirection="column" paddingX={1} paddingY={0} flexGrow={1} overflow="hidden">
      {/* Title */}
      <Box justifyContent="space-between" marginBottom={1} flexShrink={0}>
        <Text color="yellow" bold wrap="truncate">
          TASK EXECUTION GRAPH — "{taskTitle || 'Autonomous Sandbox Review & Verification'}"
        </Text>
        <Text color="gray" flexShrink={0}>
          [{defaultNodes.length} Steps]
        </Text>
      </Box>

      {/* Node List */}
      <Box flexDirection="column" flexGrow={1} overflow="hidden">
        {visibleNodes.map((node, index) => {
          const isSelected = index === selectedIndex;
          const isChild = Boolean(node.parentId);
          const indent = isChild ? '       |- ' : '  ';

          return (
            <Box key={node.id} gap={1} flexShrink={0}>
              <Text color={isSelected ? 'yellow' : 'gray'}>
                {isSelected ? '>' : ' '}
                {indent}[{node.id}]
              </Text>

              <Text
                color={
                  isSelected
                    ? 'yellow'
                    : node.status === 'running'
                    ? 'yellow'
                    : node.status === 'done' || (node.status as string) === 'completed'
                    ? 'white'
                    : 'gray'
                }
                bold={isSelected || node.status === 'running'}
                underline={isSelected}
                wrap="truncate"
              >
                {node.label}
              </Text>

              {node.detail && <Text color="gray" wrap="truncate">({node.detail})</Text>}

              <Box flexGrow={1} />

              {getStatusBadge(node.status)}
            </Box>
          );
        })}
      </Box>

      {/* Selected Node Details Card */}
      {defaultNodes[selectedIndex] && (
        <Box
          marginTop={1}
          paddingX={1}
          borderStyle="single"
          borderColor="magenta"
          justifyContent="space-between"
          flexShrink={0}
        >
          <Box gap={1} flexShrink={1}>
            <Text color="yellow" bold>Node Detail:</Text>
            <Text color="white" wrap="truncate">{defaultNodes[selectedIndex].detail || defaultNodes[selectedIndex].label}</Text>
          </Box>
          <Text color="gray" flexShrink={0}>Step {selectedIndex + 1}/{defaultNodes.length}</Text>
        </Box>
      )}

      {/* Keyboard Shortcuts Hint */}
      <Box marginTop={0} gap={3} flexShrink={0}>
        <Text color="gray">up/down: navigate</Text>
        <Text color="magenta">/diff: switch view</Text>
        <Text color="yellow">/approve: push to github</Text>
      </Box>
    </Box>
  );
};


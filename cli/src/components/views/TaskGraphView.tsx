import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';
import { TaskGraphNode } from '../../api/apiTypes.js';
import { SYMBOLS } from '../../utils/ansi.js';

interface TaskGraphViewProps {
  taskTitle: string;
  nodes: TaskGraphNode[];
  onSelectNode?: (node: TaskGraphNode) => void;
}

export const TaskGraphView: React.FC<TaskGraphViewProps> = ({
  taskTitle,
  nodes,
  onSelectNode
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const defaultNodes: TaskGraphNode[] = nodes && nodes.length > 0 ? nodes : [
    { id: '1', label: 'Scan repository workspace', status: 'done', detail: '5 source files' },
    { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols mapped' },
    { id: '3', label: 'Execute verification test suite', status: 'running', detail: 'Pytest harness active' },
    { id: '4', label: 'Gemini AI code review', status: 'pending', detail: 'Waiting for artifacts' },
    { id: '5', label: 'Generate structured report', status: 'pending', detail: 'Docs/codebase_review.md' }
  ];

  useInput((input, key) => {
    if (key.downArrow) {
      setSelectedIndex((prev) => Math.min(prev + 1, defaultNodes.length - 1));
    } else if (key.upArrow) {
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (key.return && onSelectNode) {
      onSelectNode(defaultNodes[selectedIndex]);
    }
  }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done':
      case 'completed':
        return <Text color="green">{SYMBOLS.DONE}</Text>;
      case 'running':
        return (
          <Text color="yellow">
            <Spinner type="dots" />
          </Text>
        );
      case 'failed':
        return <Text color="red">{SYMBOLS.FAILED}</Text>;
      default:
        return <Text color="gray">{SYMBOLS.PENDING}</Text>;
    }
  };

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      <Text color="cyan" bold>
        Task Graph — "{taskTitle || 'Autonomous Sandbox Review & Verification'}"
      </Text>

      <Box flexDirection="column" marginY={1}>
        {defaultNodes.map((node, index) => {
          const isSelected = index === selectedIndex;
          const isChild = Boolean(node.parentId);
          const indent = isChild ? '       ├─ ' : '  ';

          return (
            <Box key={node.id} gap={1}>
              <Text color={isSelected ? 'magenta' : 'gray'}>
                {isSelected ? '>' : ' '}
                {indent}[{node.id}]
              </Text>

              <Text
                color={isSelected ? 'magenta' : node.status === 'running' ? 'yellow' : (node.status === 'done' || node.status === 'completed') ? 'white' : 'gray'}
                bold={isSelected || node.status === 'running'}
                underline={isSelected}
              >
                {node.label}
              </Text>

              {node.detail && <Text color="gray">({node.detail})</Text>}

              <Text color="gray">.....................</Text>

              {getStatusIcon(node.status)}

              <Text color={node.status === 'running' ? 'yellow' : (node.status === 'done' || node.status === 'completed') ? 'green' : node.status === 'failed' ? 'red' : 'gray'}>
                {node.status}
              </Text>
            </Box>
          );
        })}
      </Box>

      {defaultNodes[selectedIndex] && defaultNodes[selectedIndex].detail && (
        <Box paddingX={1} borderStyle="single" borderColor="gray">
          <Text color="gray">Node Detail: </Text>
          <Text color="white">{defaultNodes[selectedIndex].detail}</Text>
        </Box>
      )}

      <Box marginTop={1} gap={3}>
        <Text color="gray">↑/↓: navigate nodes</Text>
        <Text color="magenta">/diff: view diff</Text>
        <Text color="magenta">/trace: view trace</Text>
        <Text color="magenta">/pause: pause execution</Text>
      </Box>
    </Box>
  );
};

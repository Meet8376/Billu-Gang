import React from 'react';
import { Box, Text } from 'ink';
import { ReviewerSummary } from '../../api/apiTypes.js';
import { formatCurrency, formatTokenCount } from '../../utils/formatters.js';

interface ReviewerSummaryViewProps {
  summary?: ReviewerSummary;
}

export const ReviewerSummaryView: React.FC<ReviewerSummaryViewProps> = ({ summary }) => {
  const data: ReviewerSummary = summary || {
    taskTitle: 'Fix off-by-one error in pagination',
    filesChangedCount: 2,
    testsPassingRatio: '330/330 passing',
    cost: 0.14,
    tokens: 42110,
    durationSeconds: 47,
    recoveryActionsCount: 1,
    completenessRationale:
      'Off-by-one corrected in get_page(); regression test now passes cleanly.',
    uncertaintyNotes: 'None flagged — full verification suite green.',
    rollbackCommand: 'ae-harness rollback fix-pagination-01'
  };

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      <Text color="green" bold>
        ✓ Patch complete — "{data.taskTitle}"
      </Text>

      <Box gap={4} marginY={1}>
        <Text color="gray">
          Files changed: <Text color="white">{data.filesChangedCount}</Text>
        </Text>
        <Text color="gray">
          Tests: <Text color="green">{data.testsPassingRatio}</Text>
        </Text>
      </Box>

      <Box gap={4}>
        <Text color="gray">
          Cost: <Text color="green">{formatCurrency(data.cost)}</Text>
        </Text>
        <Text color="gray">
          Tokens: <Text color="white">{formatTokenCount(data.tokens)}</Text>
        </Text>
        <Text color="gray">
          Duration: <Text color="yellow">{data.durationSeconds}s</Text>
        </Text>
        <Text color="gray">
          Recovery actions: <Text color="magenta">{data.recoveryActionsCount}</Text>
        </Text>
      </Box>

      <Box flexDirection="column" marginTop={1}>
        <Text color="cyan" bold>
          Why it's complete:
        </Text>
        <Text color="white">  {data.completenessRationale}</Text>
      </Box>

      <Box flexDirection="column" marginTop={1}>
        <Text color="yellow" bold>
          Remaining uncertainty:
        </Text>
        <Text color="white">  {data.uncertaintyNotes}</Text>
      </Box>

      <Box flexDirection="column" marginTop={1}>
        <Text color="red" bold>
          Rollback:
        </Text>
        <Text color="gray">  {data.rollbackCommand}</Text>
      </Box>

      <Box marginTop={1} gap={2}>
        <Text color="gray">⏎ /rollback: apply rollback</Text>
        <Text color="gray">⏎ /trace: full trace</Text>
      </Box>
    </Box>
  );
};

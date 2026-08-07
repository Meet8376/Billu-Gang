import React from 'react';
import { Box, Text } from 'ink';
import { ReviewerSummary } from '../../api/apiTypes.js';
import { formatCurrency, formatTokenCount, formatElapsedTime } from '../../utils/formatters.js';

interface ReviewerSummaryViewProps {
  summary?: ReviewerSummary;
  onApplyPatch?: () => void;
  onDiscardPatch?: () => void;
}

export const ReviewerSummaryView: React.FC<ReviewerSummaryViewProps> = ({
  summary,
  onApplyPatch,
  onDiscardPatch
}) => {
  const data: ReviewerSummary = summary || {
    taskTitle: 'Fix off-by-one error in pagination',
    filesChangedCount: 2,
    testsPassingRatio: '330/330 passing',
    cost: 0.14,
    tokens: 42110,
    durationSeconds: 47,
    recoveryActionsCount: 1,
    completenessRationale:
      'Off-by-one corrected in get_page(); regression test now passes.',
    uncertaintyNotes: 'None flagged — full suite green.',
    rollbackCommand: 'ae-harness rollback fix-pagination-01'
  };

  return (
    <Box flexDirection="column" padding={1} minHeight={12}>
      {/* Title */}
      <Text color="green" bold>
        ✓ Patch complete — "{data.taskTitle}"
      </Text>

      {/* Metrics Grid */}
      <Box flexDirection="column" marginY={1} paddingX={1} borderStyle="single" borderColor="gray">
        <Box gap={6}>
          <Text color="gray">
            Files changed: <Text color="white" bold>{data.filesChangedCount}</Text>
          </Text>
          <Text color="gray">
            Tests: <Text color="green" bold>{data.testsPassingRatio}</Text>
          </Text>
        </Box>

        <Box gap={6} marginTop={1}>
          <Text color="gray">
            Cost: <Text color="green" bold>{formatCurrency(data.cost)}</Text>
          </Text>
          <Text color="gray">
            Tokens: <Text color="white" bold>{formatTokenCount(data.tokens)}</Text>
          </Text>
          <Text color="gray">
            Duration: <Text color="yellow" bold>{formatElapsedTime(data.durationSeconds)}</Text>
          </Text>
          <Text color="gray">
            Recovery actions: <Text color="magenta" bold>{data.recoveryActionsCount}</Text>
          </Text>
        </Box>
      </Box>

      {/* Section 1: Why complete */}
      <Box flexDirection="column" marginTop={1}>
        <Text color="cyan" bold>
          Why it's complete:
        </Text>
        <Text color="white">  {data.completenessRationale}</Text>
      </Box>

      {/* Section 2: Remaining uncertainty */}
      <Box flexDirection="column" marginTop={1}>
        <Text color="yellow" bold>
          Remaining uncertainty:
        </Text>
        <Text color="white">  {data.uncertaintyNotes}</Text>
      </Box>

      {/* Section 3: Rollback Command */}
      <Box flexDirection="column" marginTop={1}>
        <Text color="red" bold>
          Rollback:
        </Text>
        <Text color="gray">  {data.rollbackCommand}</Text>
      </Box>

      {/* Actions footer */}
      <Box marginTop={1} gap={3}>
        <Text color="green">⏎ /apply: apply patch</Text>
        <Text color="red">⏎ /rollback: discard & rollback</Text>
        <Text color="magenta">⏎ /trace: view full trace</Text>
      </Box>
    </Box>
  );
};

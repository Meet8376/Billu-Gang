import React from 'react';
import { Box, Text } from 'ink';
import Spinner from 'ink-spinner';

export interface StageStatus {
  id: string;
  name: string;
  status: 'completed' | 'running' | 'pending' | 'failed';
  detail?: string;
}

export interface IntakeStep {
  id: string;
  step: string;
  completed: boolean;
  running?: boolean;
  detail?: string;
}

interface IntakeViewProps {
  stages?: StageStatus[];
  steps?: IntakeStep[];
  ready?: boolean;
  liveLogs?: string[];
  finalSummary?: {
    score?: number;
    testsPassing?: string;
    executionTimeSec?: number;
    reportPath?: string;
  };
}

export const IntakeView: React.FC<IntakeViewProps> = ({ stages, steps, liveLogs, finalSummary }) => {
  let displayStages: StageStatus[] = [];

  if (stages && stages.length > 0) {
    displayStages = stages;
  } else if (steps && steps.length > 0) {
    displayStages = steps.map((st) => ({
      id: st.id,
      name: st.step,
      status: st.completed ? 'completed' : st.running ? 'running' : 'pending',
      detail: st.detail,
    }));
  }

  const activeLogs = liveLogs || [];

  return (
    <Box flexDirection="column" padding={1} minHeight={16}>
      {/* Execution Progress Section */}
      <Box flexDirection="column" marginBottom={1}>
        <Text color="cyan" bold>
          --- Execution Progress ---
        </Text>
        <Box flexDirection="column" marginY={1}>
          {displayStages.length > 0 ? (
            displayStages.map((stg) => (
              <Box key={stg.id} gap={1}>
                {stg.status === 'completed' ? (
                  <Text color="green">✓</Text>
                ) : stg.status === 'running' ? (
                  <Text color="yellow">
                    <Spinner type="dots" />
                  </Text>
                ) : stg.status === 'failed' ? (
                  <Text color="red">✗</Text>
                ) : (
                  <Text color="gray">⏳</Text>
                )}

                <Text
                  color={
                    stg.status === 'completed'
                      ? 'white'
                      : stg.status === 'running'
                      ? 'yellow'
                      : stg.status === 'failed'
                      ? 'red'
                      : 'gray'
                  }
                  bold={stg.status === 'running'}
                >
                  {stg.name}
                </Text>

                {stg.detail && <Text color="gray">({stg.detail})</Text>}
              </Box>
            ))
          ) : (
            <Text color="gray">Initializing workspace stages...</Text>
          )}
        </Box>
      </Box>

      {/* Live Logs Section */}
      <Box flexDirection="column" borderStyle="single" borderColor="gray" paddingX={1} marginBottom={1}>
        <Text color="yellow" bold>
          --- Live Logs ---
        </Text>
        {activeLogs.length > 0 ? (
          activeLogs.slice(-6).map((log, idx) => (
            <Text key={idx} color="gray">
              {log}
            </Text>
          ))
        ) : (
          <Text color="gray">[System] Awaiting execution stream logs...</Text>
        )}
      </Box>

      {/* Final Summary Section (Only rendered when actual summary is present) */}
      {finalSummary && (
        <Box flexDirection="column" borderStyle="double" borderColor="green" paddingX={1}>
          <Text color="green" bold>
            --- Final Summary ---
          </Text>
          <Box gap={3} marginY={0}>
            {finalSummary.score !== undefined && (
              <Text color="gray">
                Score: <Text color="green" bold>{finalSummary.score}/100</Text>
              </Text>
            )}
            {finalSummary.score !== undefined && finalSummary.testsPassing && <Text color="gray">|</Text>}
            {finalSummary.testsPassing && (
              <Text color="gray">
                Tests: <Text color="cyan" bold>{finalSummary.testsPassing}</Text>
              </Text>
            )}
            {finalSummary.executionTimeSec !== undefined && <Text color="gray">|</Text>}
            {finalSummary.executionTimeSec !== undefined && (
              <Text color="gray">
                Execution Time: <Text color="white" bold>{finalSummary.executionTimeSec}s</Text>
              </Text>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

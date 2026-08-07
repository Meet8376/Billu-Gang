import React, { useState, useEffect } from 'react';
import { Box, Text, useInput, useStdout } from 'ink';
import { HeaderBar } from './HeaderBar.js';
import { StatusStrip } from './StatusStrip.js';
import { CommandLine } from './CommandLine.js';
import { ApprovalPrompt } from './ApprovalPrompt.js';
import { TaskGraphView } from './views/TaskGraphView.js';
import { DiffView } from './views/DiffView.js';
import { SessionInfo, TaskGraphNode } from '../api/apiTypes.js';

export type ActiveView = 'graph' | 'diff';

export function useTerminalSize() {
  const { stdout } = useStdout();
  const [size, setSize] = useState({
    columns: stdout?.columns || process.stdout.columns || 80,
    rows: stdout?.rows || process.stdout.rows || 24
  });

  useEffect(() => {
    const handleResize = () => {
      const cols = stdout?.columns || process.stdout.columns || 80;
      const rws = stdout?.rows || process.stdout.rows || 24;
      setSize({ columns: cols, rows: rws });
    };

    handleResize();
    stdout?.on('resize', handleResize);
    process.stdout?.on('resize', handleResize);

    return () => {
      stdout?.off('resize', handleResize);
      process.stdout?.off('resize', handleResize);
    };
  }, [stdout]);

  return size;
}

interface LayoutProps {
  session: SessionInfo;
  onCommandSubmit: (cmd: string) => void;
  taskTitle: string;
  taskNodes: TaskGraphNode[];
  activeViewOverride?: ActiveView;
  diffFileFilter?: string;
  pendingApproval?: { command: string; reason: string };
  onApprovalResponse?: (approved: boolean) => void;
}

export const Layout: React.FC<LayoutProps> = ({
  session,
  onCommandSubmit,
  taskTitle,
  taskNodes,
  activeViewOverride,
  diffFileFilter,
  pendingApproval,
  onApprovalResponse
}) => {
  const [activeView, setActiveView] = useState<ActiveView>('graph');
  const { columns, rows } = useTerminalSize();

  const currentView = activeViewOverride || activeView;

  useInput(
    (input, key) => {
      if (key.tab) {
        setActiveView((prev) => (prev === 'graph' ? 'diff' : 'graph'));
      }
    },
    { isActive: true }
  );

  const handleCommand = (cmd: string) => {
    const trimmed = cmd.toLowerCase().trim();
    if (trimmed.startsWith('/plan') || trimmed.startsWith('/graph') || trimmed.startsWith('/tasks')) {
      setActiveView('graph');
    } else if (trimmed.startsWith('/diff') || trimmed.startsWith('/patch')) {
      setActiveView('diff');
    }
    onCommandSubmit(cmd);
  };

  // Calculate dynamic line bounds to eliminate flickering
  const availableContentRows = Math.max(5, rows - 12);

  const renderMainPane = () => {
    switch (currentView) {
      case 'graph':
        return (
          <TaskGraphView
            taskTitle={taskTitle}
            nodes={taskNodes}
            maxVisibleNodes={availableContentRows}
          />
        );
      case 'diff':
        return (
          <DiffView
            activeFileFilter={diffFileFilter}
            maxDiffLines={availableContentRows}
          />
        );
      default:
        return (
          <TaskGraphView
            taskTitle={taskTitle}
            nodes={taskNodes}
            maxVisibleNodes={availableContentRows}
          />
        );
    }
  };

  return (
    <Box flexDirection="column" width={columns} height={rows} overflow="hidden">
      {/* 1. ROYAL HEADER BAR */}
      <HeaderBar session={session} activeView={currentView} />

      {/* 2. VIEW SWITCHER TABS BAR */}
      <Box paddingX={1} marginY={0} gap={2}>
        <Box gap={1}>
          <Text
            color={currentView === 'graph' ? 'yellow' : 'gray'}
            bold={currentView === 'graph'}
            underline={currentView === 'graph'}
          >
            [ ❖ Task Graph {currentView === 'graph' ? '(Active)' : ''} ]
          </Text>
        </Box>
        <Box gap={1}>
          <Text
            color={currentView === 'diff' ? 'yellow' : 'gray'}
            bold={currentView === 'diff'}
            underline={currentView === 'diff'}
          >
            [ ✦ Diff View {currentView === 'diff' ? '(Active)' : ''} ]
          </Text>
        </Box>
      </Box>

      {/* 3. MAIN PANE */}
      <Box
        flexGrow={1}
        borderStyle="round"
        borderColor={currentView === 'graph' ? 'yellow' : 'cyan'}
        flexDirection="column"
        overflow="hidden"
      >
        {pendingApproval ? (
          <ApprovalPrompt
            commandToApprove={pendingApproval.command}
            reason={pendingApproval.reason}
            repoName={session.repoName}
            branch={session.branch}
            onRespond={onApprovalResponse || (() => {})}
          />
        ) : (
          renderMainPane()
        )}
      </Box>

      {/* 4. ROYAL STATUS STRIP */}
      <StatusStrip session={session} currentTaskLabel={taskTitle} />

      {/* 5. ROYAL COMMAND / INPUT LINE */}
      <CommandLine onSubmit={handleCommand} disabled={Boolean(pendingApproval)} />
    </Box>
  );
};

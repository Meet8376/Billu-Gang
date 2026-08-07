import React, { useState } from 'react';
import { Box, useInput } from 'ink';
import { HeaderBar } from './HeaderBar.js';
import { StatusStrip } from './StatusStrip.js';
import { CommandLine } from './CommandLine.js';
import { ApprovalPrompt } from './ApprovalPrompt.js';
import { IntakeView, IntakeStep, StageStatus } from './views/IntakeView.js';
import { TaskGraphView } from './views/TaskGraphView.js';
import { DiffView } from './views/DiffView.js';
import { TraceView } from './views/TraceView.js';
import { ReviewerSummaryView } from './views/ReviewerSummaryView.js';
import { MemoryInspectView } from './views/MemoryInspectView.js';
import { BenchmarkView } from './views/BenchmarkView.js';
import { SessionInfo, TaskGraphNode, MemoryItem } from '../api/apiTypes.js';

export type ActiveView = 'intake' | 'graph' | 'diff' | 'trace' | 'summary' | 'memory' | 'benchmark';

interface LayoutProps {
  session: SessionInfo;
  onCommandSubmit: (cmd: string) => void;
  intakeSteps: IntakeStep[];
  intakeReady: boolean;
  taskTitle: string;
  taskNodes: TaskGraphNode[];
  memoryItems?: MemoryItem[];
  stages?: StageStatus[];
  liveLogs?: string[];
  finalSummary?: {
    score?: number;
    testsPassing?: string;
    executionTimeSec?: number;
    reportPath?: string;
  };
  activeViewOverride?: ActiveView;
  diffFileFilter?: string;
  pendingApproval?: { command: string; reason: string };
  onApprovalResponse?: (approved: boolean) => void;
}

export const Layout: React.FC<LayoutProps> = ({
  session,
  onCommandSubmit,
  intakeSteps,
  intakeReady,
  taskTitle,
  taskNodes,
  memoryItems,
  stages,
  liveLogs,
  finalSummary,
  activeViewOverride,
  diffFileFilter,
  pendingApproval,
  onApprovalResponse
}) => {
  const [activeView, setActiveView] = useState<ActiveView>('intake');

  const currentView = activeViewOverride || activeView;

  useInput((input, key) => {
    if (key.tab) {
      const views: ActiveView[] = ['intake', 'graph', 'diff', 'trace', 'summary', 'memory', 'benchmark'];
      const currentIndex = views.indexOf(currentView);
      const nextIndex = (currentIndex + 1) % views.length;
      setActiveView(views[nextIndex]);
    }
  }, { isActive: true });

  const handleCommand = (cmd: string) => {
    const trimmed = cmd.toLowerCase().trim();
    if (trimmed.startsWith('/plan') || trimmed.startsWith('/graph')) {
      setActiveView('graph');
    } else if (trimmed.startsWith('/diff')) {
      setActiveView('diff');
    } else if (trimmed.startsWith('/trace') || trimmed.startsWith('/logs')) {
      setActiveView('trace');
    } else if (trimmed.startsWith('/summary') || trimmed.startsWith('/review')) {
      setActiveView('summary');
    } else if (trimmed.startsWith('/memory')) {
      setActiveView('memory');
    } else if (trimmed.startsWith('/benchmark') || trimmed.startsWith('/eval')) {
      setActiveView('benchmark');
    } else if (trimmed.startsWith('/intake')) {
      setActiveView('intake');
    }
    onCommandSubmit(cmd);
  };

  const renderMainPane = () => {
    switch (currentView) {
      case 'intake':
        return <IntakeView steps={intakeSteps} ready={intakeReady} stages={stages} liveLogs={liveLogs} finalSummary={finalSummary} />;
      case 'graph':
        return <TaskGraphView taskTitle={taskTitle} nodes={taskNodes} />;
      case 'diff':
        return <DiffView activeFileFilter={diffFileFilter} />;
      case 'trace':
        return <TraceView />;
      case 'summary':
        return <ReviewerSummaryView />;
      case 'memory':
        return <MemoryInspectView memoryItems={memoryItems} />;
      case 'benchmark':
        return <BenchmarkView />;
      default:
        return <IntakeView steps={intakeSteps} ready={intakeReady} stages={stages} liveLogs={liveLogs} finalSummary={finalSummary} />;
    }
  };

  return (
    <Box flexDirection="column" width="100%" height="100%">
      {/* 1. HEADER BAR */}
      <HeaderBar session={session} activeView={currentView} />

      {/* 2. MAIN PANE */}
      <Box flexGrow={1} borderStyle="single" borderColor="blue" flexDirection="column">
        {pendingApproval ? (
          <ApprovalPrompt
            commandToApprove={pendingApproval.command}
            reason={pendingApproval.reason}
            onRespond={onApprovalResponse || (() => {})}
          />
        ) : (
          renderMainPane()
        )}
      </Box>

      {/* 3. STATUS STRIP */}
      <StatusStrip session={session} currentTaskLabel={taskTitle} />

      {/* 4. COMMAND / INPUT LINE */}
      <CommandLine onSubmit={handleCommand} disabled={Boolean(pendingApproval)} />
    </Box>
  );
};

import { ParsedSlashCommand } from './SlashCommandRouter.js';
import { BackendApiClient } from '../api/BackendApiClient.js';

export interface CommandExecutionResult {
  handledLocally: boolean;
  activeViewTarget?: 'intake' | 'graph' | 'diff' | 'trace' | 'summary' | 'memory' | 'benchmark';
  fileFilter?: string;
  feedbackMessage?: string;
}

export async function handleSlashCommand(
  cmd: ParsedSlashCommand,
  sessionId: string,
  apiClient: BackendApiClient
): Promise<CommandExecutionResult> {
  switch (cmd.type) {
    case 'intake':
      return {
        handledLocally: true,
        activeViewTarget: 'intake',
        feedbackMessage: 'Switched to Repository Intake View.'
      };

    case 'plan':
      return {
        handledLocally: true,
        activeViewTarget: 'graph',
        feedbackMessage: 'Switched to Task Graph View.'
      };

    case 'diff':
      return {
        handledLocally: true,
        activeViewTarget: 'diff',
        fileFilter: cmd.filterArg,
        feedbackMessage: cmd.filterArg
          ? `Switched to Diff View (filter: ${cmd.filterArg}).`
          : 'Switched to Diff View.'
      };

    case 'trace':
      return {
        handledLocally: true,
        activeViewTarget: 'trace',
        feedbackMessage: 'Switched to Trace View.'
      };

    case 'summary':
      return {
        handledLocally: true,
        activeViewTarget: 'summary',
        feedbackMessage: 'Switched to Reviewer Summary View.'
      };

    case 'memory':
      const items = await apiClient.fetchMemoryItems(sessionId);
      return {
        handledLocally: true,
        activeViewTarget: 'memory',
        feedbackMessage: `Switched to Memory Inspect View (${items.length} items loaded).`
      };

    case 'benchmark':
      return {
        handledLocally: true,
        activeViewTarget: 'benchmark',
        feedbackMessage: 'Switched to Benchmark Evaluation View.'
      };

    case 'rollback':
      const res = await apiClient.rollbackSession(sessionId);
      return {
        handledLocally: true,
        feedbackMessage: `Rollback: ${res.message}`
      };

    case 'pause':
      return {
        handledLocally: true,
        feedbackMessage: 'Session execution paused.'
      };

    case 'help':
      return {
        handledLocally: true,
        feedbackMessage:
          'Available slash commands: /intake, /plan, /diff [file], /trace, /summary, /memory, /benchmark, /rollback, /pause'
      };

    default:
      return {
        handledLocally: false,
        feedbackMessage: `Unrecognized command: ${cmd.rawInput}`
      };
  }
}

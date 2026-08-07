import { ParsedSlashCommand } from './SlashCommandRouter.js';
import { BackendApiClient } from '../api/BackendApiClient.js';
export interface CommandExecutionResult {
    handledLocally: boolean;
    activeViewTarget?: 'intake' | 'graph' | 'diff' | 'trace' | 'summary' | 'memory';
    fileFilter?: string;
    feedbackMessage?: string;
}
export declare function handleSlashCommand(cmd: ParsedSlashCommand, sessionId: string, apiClient: BackendApiClient): Promise<CommandExecutionResult>;

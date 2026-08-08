import { ParsedSlashCommand } from './SlashCommandRouter.js';
import { BackendApiClient } from '../api/BackendApiClient.js';
import { MemoryItem } from '../api/apiTypes.js';
export interface CommandExecutionResult {
    handledLocally: boolean;
    activeViewTarget?: 'graph' | 'diff';
    fileFilter?: string;
    feedbackMessage?: string;
    memoryItems?: MemoryItem[];
}
export declare function handleSlashCommand(cmd: ParsedSlashCommand, sessionId: string, apiClient: BackendApiClient): Promise<CommandExecutionResult>;

export type SlashCommandType = 'intake' | 'plan' | 'diff' | 'trace' | 'memory' | 'rollback' | 'approve' | 'pause' | 'help' | 'unknown';
export interface ParsedSlashCommand {
    type: SlashCommandType;
    rawInput: string;
    commandName: string;
    args: string[];
    filterArg?: string;
}
export declare class SlashCommandRouter {
    static parse(input: string): ParsedSlashCommand;
    static getSuggestions(input: string): string[];
}

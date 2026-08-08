import { SessionInfo, MemoryItem } from './apiTypes.js';
export declare class BackendApiClient {
    private baseUrl;
    constructor(baseUrl?: string);
    createSession(repoPath: string, model: string): Promise<SessionInfo>;
    submitIssue(sessionId: string, issueDescription: string, modelName?: string, workspacePath?: string): Promise<{
        success: boolean;
        data?: any;
    }>;
    fetchMemoryItems(sessionId: string): Promise<MemoryItem[]>;
    rollbackSession(sessionId: string): Promise<{
        success: boolean;
        message: string;
    }>;
}

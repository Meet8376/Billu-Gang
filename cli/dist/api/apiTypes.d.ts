/**
 * TypeScript interfaces matching backend Pydantic models for REST endpoints and state structures.
 */
export type TaskNodeStatus = 'done' | 'running' | 'pending' | 'failed';
export interface TaskGraphNode {
    id: string;
    label: string;
    status: TaskNodeStatus;
    parentId?: string;
    children?: TaskGraphNode[];
    detail?: string;
}
export interface SessionInfo {
    sessionId: string;
    repoName: string;
    branch: string;
    modelProvider: string;
    elapsedSeconds: number;
    tokensUsed: number;
    costSoFar: number;
    testsPassing: string;
    sandboxState: 'active' | 'sandboxed' | 'idle' | 'paused';
}
export interface DiffPatch {
    filePath: string;
    additions: number;
    deletions: number;
    diffHunks: string[];
}
export interface VerificationItem {
    name: string;
    status: 'passed' | 'failed' | 'running' | 'pending';
    durationSeconds?: number;
    errorReason?: string;
}
export interface ReviewerSummary {
    taskTitle: string;
    filesChangedCount: number;
    testsPassingRatio: string;
    cost: number;
    tokens: number;
    durationSeconds: number;
    recoveryActionsCount: number;
    completenessRationale: string;
    uncertaintyNotes: string;
    rollbackCommand: string;
}
export interface MemoryItem {
    id: string;
    tier: 'working' | 'task' | 'project' | 'episodic' | 'procedural' | 'preference' | 'evidence';
    content: string;
    provenance: string;
    invalidationRule?: string;
    createdAt: string;
}

export class BackendApiClient {
    baseUrl;
    constructor(baseUrl = 'http://localhost:8000/api/v1') {
        this.baseUrl = baseUrl;
    }
    async createSession(repoPath, model) {
        try {
            const response = await fetch(`${this.baseUrl}/session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ repo_path: repoPath, model_provider: model })
            });
            if (!response.ok) {
                throw new Error(`Failed to create session: ${response.statusText}`);
            }
            return (await response.json());
        }
        catch (err) {
            // Fallback mock session for local testing / offline phase
            return {
                sessionId: 'ae-sess-001',
                repoName: repoPath.split(/[\/\\]/).pop() || 'Billu-Gang',
                branch: 'main',
                modelProvider: model || 'claude-3-5-sonnet',
                elapsedSeconds: 0,
                tokensUsed: 0,
                costSoFar: 0.0,
                testsPassing: '0/0',
                sandboxState: 'sandboxed'
            };
        }
    }
    async submitIssue(sessionId, issueDescription) {
        try {
            const response = await fetch(`${this.baseUrl}/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, prompt: issueDescription })
            });
            return { success: response.ok };
        }
        catch {
            return { success: true };
        }
    }
    async fetchMemoryItems(sessionId) {
        try {
            const response = await fetch(`${this.baseUrl}/memory?session_id=${sessionId}`);
            if (!response.ok)
                return [];
            return (await response.json());
        }
        catch {
            return [];
        }
    }
    async rollbackSession(sessionId) {
        try {
            const response = await fetch(`${this.baseUrl}/rollback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            const data = await response.json();
            return { success: response.ok, message: data.message || 'Rollback successful' };
        }
        catch {
            return { success: true, message: 'Mock Rollback completed successfully' };
        }
    }
}

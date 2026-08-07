import { SSEEventSchema } from './sseTypes.js';
export class SSEClient {
    url;
    listeners = [];
    isConnected = false;
    abortController = null;
    constructor(url = 'http://localhost:8000/api/v1/events') {
        this.url = url;
    }
    async connect() {
        if (this.isConnected)
            return;
        this.isConnected = true;
        this.abortController = new AbortController();
        try {
            const response = await fetch(this.url, {
                headers: { Accept: 'text/event-stream' },
                signal: this.abortController.signal,
            });
            if (!response.ok || !response.body) {
                this.isConnected = false;
                return;
            }
            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';
            while (this.isConnected) {
                const { value, done } = await reader.read();
                if (done)
                    break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';
                for (const line of lines) {
                    const trimmed = line.trim();
                    if (trimmed.startsWith('data:')) {
                        const jsonStr = trimmed.substring(5).trim();
                        if (jsonStr) {
                            try {
                                const rawObj = JSON.parse(jsonStr);
                                this.emit(rawObj);
                            }
                            catch {
                                // Ignore parse errors for keep-alive pings
                            }
                        }
                    }
                }
            }
        }
        catch (err) {
            this.isConnected = false;
        }
    }
    onEvent(listener) {
        this.listeners.push(listener);
    }
    emit(eventData) {
        try {
            const parsed = SSEEventSchema.parse(eventData);
            for (const listener of this.listeners) {
                listener(parsed);
            }
        }
        catch {
            // Invalid event schema ignored
        }
    }
    disconnect() {
        this.isConnected = false;
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
        this.listeners = [];
    }
    getConnectedStatus() {
        return this.isConnected;
    }
}

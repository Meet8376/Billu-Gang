import { SSEEventSchema } from './sseTypes.js';
export class SSEClient {
    url;
    listeners = [];
    isConnected = false;
    constructor(url = 'http://localhost:8000/api/v1/events') {
        this.url = url;
    }
    connect() {
        this.isConnected = true;
        // In actual environment EventSource connects to backend endpoint
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
        catch (err) {
            // Invalid event schema ignored or logged in debug mode
        }
    }
    disconnect() {
        this.isConnected = false;
        this.listeners = [];
    }
    getConnectedStatus() {
        return this.isConnected;
    }
}

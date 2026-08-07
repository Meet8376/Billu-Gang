import { SSEEvent, SSEEventSchema } from './sseTypes.js';

export type SSEEventListener = (event: SSEEvent) => void;

export class SSEClient {
  private url: string;
  private listeners: SSEEventListener[] = [];
  private isConnected: boolean = false;

  constructor(url: string = 'http://localhost:8000/api/v1/events') {
    this.url = url;
  }

  connect() {
    this.isConnected = true;
    // In actual environment EventSource connects to backend endpoint
  }

  onEvent(listener: SSEEventListener) {
    this.listeners.push(listener);
  }

  emit(eventData: any) {
    try {
      const parsed = SSEEventSchema.parse(eventData);
      for (const listener of this.listeners) {
        listener(parsed);
      }
    } catch (err) {
      // Invalid event schema ignored or logged in debug mode
    }
  }

  disconnect() {
    this.isConnected = false;
    this.listeners = [];
  }

  getConnectedStatus(): boolean {
    return this.isConnected;
  }
}

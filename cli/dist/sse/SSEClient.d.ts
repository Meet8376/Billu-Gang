import { SSEEvent } from './sseTypes.js';
export type SSEEventListener = (event: SSEEvent) => void;
export declare class SSEClient {
    private url;
    private listeners;
    private isConnected;
    private abortController;
    constructor(url?: string);
    connect(): Promise<void>;
    onEvent(listener: SSEEventListener): void;
    emit(eventData: any): void;
    disconnect(): void;
    getConnectedStatus(): boolean;
}

import { SSEEvent } from './sseTypes.js';
export type SSEEventListener = (event: SSEEvent) => void;
export declare class SSEClient {
    private url;
    private listeners;
    private isConnected;
    constructor(url?: string);
    connect(): void;
    onEvent(listener: SSEEventListener): void;
    emit(eventData: any): void;
    disconnect(): void;
    getConnectedStatus(): boolean;
}

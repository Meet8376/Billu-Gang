import { SSEClient } from './SSEClient.js';
import { SSEEvent } from './sseTypes.js';
export declare function startMockSSEStream(sseClient: SSEClient, onEvent: (evt: SSEEvent) => void): void;

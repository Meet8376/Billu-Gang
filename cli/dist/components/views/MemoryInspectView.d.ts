import React from 'react';
import { MemoryItem } from '../../api/apiTypes.js';
export type MemoryTierFilter = 'all' | 'working' | 'task' | 'project' | 'episodic' | 'procedural' | 'preference' | 'evidence';
interface MemoryInspectViewProps {
    memoryItems?: MemoryItem[];
    onDeleteItem?: (id: string) => void;
    onExportMemory?: () => void;
}
export declare const MemoryInspectView: React.FC<MemoryInspectViewProps>;
export {};

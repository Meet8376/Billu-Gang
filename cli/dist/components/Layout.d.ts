import React from 'react';
import { SessionInfo, TaskGraphNode } from '../api/apiTypes.js';
export type ActiveView = 'graph' | 'diff';
export declare function useTerminalSize(): {
    columns: number;
    rows: number;
};
interface LayoutProps {
    session: SessionInfo;
    onCommandSubmit: (cmd: string) => void;
    taskTitle: string;
    taskNodes: TaskGraphNode[];
    activeViewOverride?: ActiveView;
    diffFileFilter?: string;
    pendingApproval?: {
        command: string;
        reason: string;
    };
    onApprovalResponse?: (approved: boolean) => void;
}
export declare const Layout: React.FC<LayoutProps>;
export {};

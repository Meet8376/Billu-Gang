import React from 'react';
import { IntakeStep } from './views/IntakeView.js';
import { SessionInfo, TaskGraphNode } from '../api/apiTypes.js';
export type ActiveView = 'intake' | 'graph' | 'diff' | 'trace' | 'summary' | 'memory';
interface LayoutProps {
    session: SessionInfo;
    onCommandSubmit: (cmd: string) => void;
    intakeSteps: IntakeStep[];
    intakeReady: boolean;
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

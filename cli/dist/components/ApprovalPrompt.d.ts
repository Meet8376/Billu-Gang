import React from 'react';
export interface PendingApprovalRequest {
    id?: string;
    command?: string;
    reason?: string;
    repoName?: string;
    branch?: string;
    requestedAt?: string;
}
interface ApprovalPromptProps {
    request?: PendingApprovalRequest;
    commandToApprove?: string;
    reason?: string;
    repoName?: string;
    branch?: string;
    onRespond: (approved: boolean) => void;
}
export declare const ApprovalPrompt: React.FC<ApprovalPromptProps>;
export {};

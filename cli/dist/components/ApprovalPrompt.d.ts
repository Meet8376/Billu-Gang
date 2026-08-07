import React from 'react';
interface ApprovalPromptProps {
    commandToApprove: string;
    reason: string;
    onRespond: (approved: boolean) => void;
}
export declare const ApprovalPrompt: React.FC<ApprovalPromptProps>;
export {};

import React from 'react';
export interface IntakeStep {
    id: string;
    step: string;
    completed: boolean;
    running?: boolean;
    detail?: string;
}
interface IntakeViewProps {
    steps: IntakeStep[];
    ready: boolean;
}
export declare const IntakeView: React.FC<IntakeViewProps>;
export {};

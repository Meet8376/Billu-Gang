import React from 'react';
import { VerificationItem } from '../../api/apiTypes.js';
interface TraceViewProps {
    verifications?: VerificationItem[];
    logs?: string[];
    recoveringReason?: string;
}
export declare const TraceView: React.FC<TraceViewProps>;
export {};

import React from 'react';
import { SessionInfo } from '../api/apiTypes.js';
interface StatusStripProps {
    session: SessionInfo;
    currentTaskLabel?: string;
}
export declare const StatusStrip: React.FC<StatusStripProps>;
export {};

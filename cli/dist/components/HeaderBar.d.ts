import React from 'react';
import { SessionInfo } from '../api/apiTypes.js';
interface HeaderBarProps {
    session: SessionInfo;
    activeView: string;
}
export declare const HeaderBar: React.FC<HeaderBarProps>;
export {};

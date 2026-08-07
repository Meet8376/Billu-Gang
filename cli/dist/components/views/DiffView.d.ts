import React from 'react';
import { DiffPatch } from '../../api/apiTypes.js';
interface DiffViewProps {
    patches?: DiffPatch[];
    activeFileFilter?: string;
}
export declare const DiffView: React.FC<DiffViewProps>;
export {};

import React from 'react';
import { ReviewerSummary } from '../../api/apiTypes.js';
interface ReviewerSummaryViewProps {
    summary?: ReviewerSummary;
    onApplyPatch?: () => void;
    onDiscardPatch?: () => void;
}
export declare const ReviewerSummaryView: React.FC<ReviewerSummaryViewProps>;
export {};

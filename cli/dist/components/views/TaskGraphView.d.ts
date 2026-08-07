import React from 'react';
import { TaskGraphNode } from '../../api/apiTypes.js';
interface TaskGraphViewProps {
    taskTitle: string;
    nodes: TaskGraphNode[];
    onSelectNode?: (node: TaskGraphNode) => void;
}
export declare const TaskGraphView: React.FC<TaskGraphViewProps>;
export {};

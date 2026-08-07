import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';
export const TaskGraphView = ({ taskTitle, nodes, maxVisibleNodes = 8, onSelectNode }) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const defaultNodes = nodes && nodes.length > 0
        ? nodes
        : [
            { id: '1', label: 'Scan repository workspace', status: 'done', detail: 'Source files indexed' },
            { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols & AST mapped' },
            { id: '3', label: 'Execute verification test suite', status: 'running', detail: 'Pytest harness active' },
            { id: '4', label: 'Gemini AI code review', status: 'pending', detail: 'Waiting for model artifacts' },
            { id: '5', label: 'Push verified patch to GitHub', status: 'pending', detail: 'git push origin main' }
        ];
    useInput((input, key) => {
        if (key.downArrow) {
            setSelectedIndex((prev) => Math.min(prev + 1, defaultNodes.length - 1));
        }
        else if (key.upArrow) {
            setSelectedIndex((prev) => Math.max(prev - 1, 0));
        }
        else if (key.return && onSelectNode) {
            onSelectNode(defaultNodes[selectedIndex]);
        }
    }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });
    const getStatusBadge = (status) => {
        switch (status) {
            case 'done':
            case 'completed':
                return _jsx(Text, { color: "green", bold: true, children: "\u2714 Done" });
            case 'running':
                return (_jsxs(Text, { color: "yellow", bold: true, children: [_jsx(Spinner, { type: "dots" }), " Executing"] }));
            case 'failed':
                return _jsx(Text, { color: "red", bold: true, children: "\u2716 Failed" });
            default:
                return _jsx(Text, { color: "gray", children: "\u25C8 Pending" });
        }
    };
    // Slice nodes for height safety to prevent terminal scrolling & flickering
    const visibleNodes = defaultNodes.slice(0, maxVisibleNodes);
    return (_jsxs(Box, { flexDirection: "column", paddingX: 1, paddingY: 0, flexGrow: 1, overflow: "hidden", children: [_jsxs(Box, { justifyContent: "space-between", marginBottom: 1, children: [_jsxs(Text, { color: "yellow", bold: true, children: ["\u2756 TASK EXECUTION GRAPH \u2014 \"", taskTitle || 'Autonomous Sandbox Review & Verification', "\""] }), _jsxs(Text, { color: "gray", children: ["[", defaultNodes.length, " Total Steps]"] })] }), _jsx(Box, { flexDirection: "column", flexGrow: 1, overflow: "hidden", children: visibleNodes.map((node, index) => {
                    const isSelected = index === selectedIndex;
                    const isChild = Boolean(node.parentId);
                    const indent = isChild ? '       ├─ ' : '  ';
                    return (_jsxs(Box, { gap: 1, children: [_jsxs(Text, { color: isSelected ? 'yellow' : 'gray', children: [isSelected ? '👑' : ' ', indent, "[", node.id, "]"] }), _jsx(Text, { color: isSelected
                                    ? 'yellow'
                                    : node.status === 'running'
                                        ? 'yellow'
                                        : node.status === 'done' || node.status === 'completed'
                                            ? 'white'
                                            : 'gray', bold: isSelected || node.status === 'running', underline: isSelected, children: node.label }), node.detail && _jsxs(Text, { color: "gray", children: ["(", node.detail, ")"] }), _jsx(Box, { flexGrow: 1 }), getStatusBadge(node.status)] }, node.id));
                }) }), defaultNodes[selectedIndex] && (_jsxs(Box, { marginTop: 1, paddingX: 1, borderStyle: "single", borderColor: "magenta", justifyContent: "space-between", children: [_jsxs(Box, { gap: 1, children: [_jsx(Text, { color: "yellow", bold: true, children: "Node Detail:" }), _jsx(Text, { color: "white", children: defaultNodes[selectedIndex].detail || defaultNodes[selectedIndex].label })] }), _jsxs(Text, { color: "gray", children: ["Step ", selectedIndex + 1, "/", defaultNodes.length] })] })), _jsxs(Box, { marginTop: 0, gap: 3, children: [_jsx(Text, { color: "gray", children: "\u2191/\u2193: navigate nodes" }), _jsx(Text, { color: "magenta", children: "/diff: switch view" }), _jsx(Text, { color: "yellow", children: "/approve: push to github" })] })] }));
};

import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';
import { SYMBOLS } from '../../utils/ansi.js';

export const TaskGraphView = ({ taskTitle, nodes, onSelectNode }) => {
    const [selectedIndex, setSelectedIndex] = useState(0);

    const defaultNodes = nodes && nodes.length > 0 ? nodes : [
        { id: '1', label: 'Scan repository workspace', status: 'done', detail: '5 source files' },
        { id: '2', label: 'Parse AST symbol graph', status: 'done', detail: 'Symbols mapped' },
        { id: '3', label: 'Execute verification test suite', status: 'running', detail: 'Pytest harness active' },
        { id: '4', label: 'Gemini AI code review', status: 'pending', detail: 'Waiting for artifacts' },
        { id: '5', label: 'Generate structured report', status: 'pending', detail: 'Docs/codebase_review.md' }
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

    const getStatusIcon = (status) => {
        switch (status) {
            case 'done':
            case 'completed':
                return _jsx(Text, { color: "green", children: SYMBOLS.DONE });
            case 'running':
                return (_jsx(Text, { color: "yellow", children: _jsx(Spinner, { type: "dots" }) }));
            case 'failed':
                return _jsx(Text, { color: "red", children: SYMBOLS.FAILED });
            default:
                return _jsx(Text, { color: "gray", children: SYMBOLS.PENDING });
        }
    };

    return (_jsxs(Box, {
        flexDirection: "column", padding: 1, minHeight: 12, children: [
            _jsxs(Text, { color: "cyan", bold: true, children: ["Task Graph \u2014 \"", taskTitle || 'Autonomous Sandbox Review & Verification', "\""] }),
            _jsx(Box, {
                flexDirection: "column", marginY: 1, children: defaultNodes.map((node, index) => {
                    const isSelected = index === selectedIndex;
                    const isChild = Boolean(node.parentId);
                    const indent = isChild ? '       ├─ ' : '  ';
                    return (_jsxs(Box, { gap: 1, children: [
                        _jsxs(Text, { color: isSelected ? 'magenta' : 'gray', children: [isSelected ? '>' : ' ', indent, "[", node.id, "]"] }),
                        _jsx(Text, { color: isSelected ? 'magenta' : node.status === 'running' ? 'yellow' : (node.status === 'done' || node.status === 'completed') ? 'white' : 'gray', bold: isSelected || node.status === 'running', underline: isSelected, children: node.label }),
                        node.detail && _jsxs(Text, { color: "gray", children: ["(", node.detail, ")"] }),
                        _jsx(Text, { color: "gray", children: "....................." }),
                        getStatusIcon(node.status),
                        _jsx(Text, { color: node.status === 'running' ? 'yellow' : (node.status === 'done' || node.status === 'completed') ? 'green' : node.status === 'failed' ? 'red' : 'gray', children: node.status })
                    ] }, node.id));
                })
            }),
            defaultNodes[selectedIndex] && defaultNodes[selectedIndex].detail && (_jsxs(Box, { paddingX: 1, borderStyle: "single", borderColor: "gray", children: [
                _jsx(Text, { color: "gray", children: "Node Detail: " }),
                _jsx(Text, { color: "white", children: defaultNodes[selectedIndex].detail })
            ] })),
            _jsxs(Box, { marginTop: 1, gap: 3, children: [
                _jsx(Text, { color: "gray", children: "\u2191/\u2193: navigate nodes" }),
                _jsx(Text, { color: "magenta", children: "/diff: view diff" }),
                _jsx(Text, { color: "magenta", children: "/trace: view trace" }),
                _jsx(Text, { color: "magenta", children: "/pause: pause execution" })
            ] })
        ]
    }));
};

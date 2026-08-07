import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Box, Text, useInput } from 'ink';
export const DiffView = ({ patches, activeFileFilter }) => {
    const defaultPatches = patches && patches.length > 0 ? patches : [
        {
            filePath: 'paginator.py',
            additions: 4,
            deletions: 2,
            diffHunks: [
                '  42   def get_page(items, page, size):',
                '  43 -     start = page * size',
                '  44 -     end = start + size',
                '  43 +     start = (page - 1) * size',
                '  44 +     end = start + size',
                '  45       return items[start:end]'
            ]
        },
        {
            filePath: 'tests/test_paginator.py',
            additions: 8,
            deletions: 0,
            diffHunks: [
                '  105   def test_pagination_first_page():',
                '  106 +     res = get_page([1, 2, 3, 4], page=1, size=2)',
                '  107 +     assert res == [1, 2]',
                '  108 +',
                '  109 + def test_pagination_last_page():',
                '  110 +     res = get_page([1, 2, 3, 4], page=2, size=2)',
                '  111 +     assert res == [3, 4]'
            ]
        }
    ];
    const filteredPatches = activeFileFilter
        ? defaultPatches.filter((p) => p.filePath.toLowerCase().includes(activeFileFilter.toLowerCase()))
        : defaultPatches;
    const [activeFileIndex, setActiveFileIndex] = useState(0);
    const currentPatch = filteredPatches[activeFileIndex] || defaultPatches[0];
    useInput((input, key) => {
        if (key.rightArrow) {
            setActiveFileIndex((prev) => (prev + 1) % filteredPatches.length);
        }
        else if (key.leftArrow) {
            setActiveFileIndex((prev) => (prev - 1 + filteredPatches.length) % filteredPatches.length);
        }
    }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });
    return (_jsxs(Box, { flexDirection: "column", padding: 1, minHeight: 12, children: [_jsx(Box, { gap: 2, marginBottom: 1, children: filteredPatches.map((p, idx) => (_jsxs(Box, { gap: 1, children: [_jsx(Text, { color: idx === activeFileIndex ? 'cyan' : 'gray', bold: idx === activeFileIndex, underline: idx === activeFileIndex, children: p.filePath }), _jsxs(Text, { children: [_jsxs(Text, { color: "green", children: ["+", p.additions] }), " ", _jsxs(Text, { color: "red", children: ["\u2212", p.deletions] })] })] }, p.filePath))) }), _jsxs(Box, { borderStyle: "single", borderColor: "blue", paddingX: 1, justifyContent: "space-between", children: [_jsx(Text, { color: "cyan", bold: true, children: currentPatch.filePath }), _jsxs(Text, { children: [_jsxs(Text, { color: "green", children: ["+", currentPatch.additions] }), ' ', _jsxs(Text, { color: "red", children: ["\u2212", currentPatch.deletions] })] })] }), _jsx(Box, { flexDirection: "column", marginY: 1, children: currentPatch.diffHunks.map((line, idx) => {
                    if (line.includes(' + ')) {
                        return (_jsx(Text, { color: "green", children: line }, idx));
                    }
                    if (line.includes(' - ')) {
                        return (_jsx(Text, { color: "red", dimColor: true, children: line }, idx));
                    }
                    return (_jsx(Text, { color: "gray", children: line }, idx));
                }) }), _jsxs(Box, { marginTop: 1, gap: 2, children: [_jsx(Text, { color: "gray", children: "\u2190/\u2192: switch file diff" }), _jsx(Text, { color: "magenta", children: "/plan: task graph" }), _jsx(Text, { color: "magenta", children: "/trace: trace logs" })] })] }));
};

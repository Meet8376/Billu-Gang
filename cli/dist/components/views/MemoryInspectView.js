import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Box, Text, useInput } from 'ink';
export const MemoryInspectView = ({ memoryItems, onDeleteItem, onExportMemory }) => {
    const defaultItems = memoryItems && memoryItems.length > 0 ? memoryItems : [
        {
            id: 'mem-01',
            tier: 'working',
            content: 'Paginator start index adjusted to (page - 1) * size',
            provenance: 'AST Indexer + Edit Step 3a | Conf: 0.98',
            invalidationRule: 'Auto-expire on paginator.py file change',
            createdAt: '2026-08-07 12:45:00'
        },
        {
            id: 'mem-02',
            tier: 'task',
            content: 'Issue report: page calculation off by one on page >= 2',
            provenance: 'User Prompt Input | Conf: 1.00',
            createdAt: '2026-08-07 12:40:00'
        },
        {
            id: 'mem-03',
            tier: 'project',
            content: 'Pytest suite configuration targets tests/ directory',
            provenance: 'repo_scanner: pytest.ini | Conf: 1.00',
            createdAt: '2026-08-07 12:35:00'
        },
        {
            id: 'mem-04',
            tier: 'episodic',
            content: 'Previous run recovered from regression test failure by re-running paginator fixture',
            provenance: 'Episodic Memory Logger | Conf: 0.92',
            invalidationRule: 'Expire after 24h session window',
            createdAt: '2026-08-07 12:30:00'
        },
        {
            id: 'mem-05',
            tier: 'procedural',
            content: 'Procedure: Always run pytest -v tests/test_paginator.py after editing paginator.py',
            provenance: 'Procedural Rule Engine | Conf: 0.95',
            createdAt: '2026-08-07 12:20:00'
        },
        {
            id: 'mem-06',
            tier: 'preference',
            content: 'User prefers concise unified diff summaries over full file output',
            provenance: 'User CLI Settings | Conf: 1.00',
            createdAt: '2026-08-07 12:10:00'
        },
        {
            id: 'mem-07',
            tier: 'evidence',
            content: 'Verification evidence: 330/330 unit tests passed cleanly inside Docker sandbox',
            provenance: 'Verification Pipeline Run #4 | Conf: 1.00',
            createdAt: '2026-08-07 12:50:00'
        }
    ];
    const tiers = [
        'all',
        'working',
        'task',
        'project',
        'episodic',
        'procedural',
        'preference',
        'evidence'
    ];
    const [selectedTierIndex, setSelectedTierIndex] = useState(0);
    const activeTier = tiers[selectedTierIndex];
    useInput((input, key) => {
        if (key.rightArrow) {
            setSelectedTierIndex((prev) => (prev + 1) % tiers.length);
        }
        else if (key.leftArrow) {
            setSelectedTierIndex((prev) => (prev - 1 + tiers.length) % tiers.length);
        }
        else if (input.toLowerCase() === 'e' && onExportMemory) {
            onExportMemory();
        }
    }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });
    const filteredItems = activeTier === 'all'
        ? defaultItems
        : defaultItems.filter((item) => item.tier === activeTier);
    return (_jsxs(Box, { flexDirection: "column", padding: 1, minHeight: 12, children: [_jsx(Text, { color: "cyan", bold: true, children: "Tiered Memory Inspection Browser (7 Core Surfaces FR9\u2013FR12)" }), _jsxs(Box, { gap: 1, marginY: 1, children: [_jsx(Text, { color: "gray", children: "Tiers: " }), tiers.map((t, idx) => (_jsxs(Text, { color: idx === selectedTierIndex ? 'magenta' : 'gray', bold: idx === selectedTierIndex, underline: idx === selectedTierIndex, children: ["[", t.toUpperCase(), "]"] }, t)))] }), _jsx(Box, { flexDirection: "column", marginY: 1, children: filteredItems.length === 0 ? (_jsxs(Text, { color: "gray", children: ["No memory items found in tier [", activeTier.toUpperCase(), "]."] })) : (filteredItems.map((item) => (_jsxs(Box, { flexDirection: "column", borderStyle: "single", borderColor: idxColor(item.tier), paddingX: 1, marginY: 1, children: [_jsxs(Box, { justifyContent: "space-between", children: [_jsxs(Text, { color: idxColor(item.tier), bold: true, children: ["[", item.tier.toUpperCase(), "] ", item.id] }), _jsx(Text, { color: "gray", children: item.createdAt })] }), _jsx(Text, { color: "white", bold: true, children: item.content }), _jsx(Box, { marginTop: 1, gap: 2, children: _jsxs(Text, { color: "yellow", children: ["Provenance: ", item.provenance] }) }), item.invalidationRule && (_jsxs(Text, { color: "red", dimColor: true, children: ["Rule: ", item.invalidationRule] }))] }, item.id)))) }), _jsxs(Box, { marginTop: 1, gap: 3, children: [_jsx(Text, { color: "gray", children: "\u2190/\u2192: cycle memory tiers" }), _jsx(Text, { color: "magenta", children: "e: export memory snapshot" }), _jsx(Text, { color: "magenta", children: "/rollback: trigger rollback" })] })] }));
};
function idxColor(tier) {
    switch (tier) {
        case 'working': return 'yellow';
        case 'task': return 'cyan';
        case 'project': return 'blue';
        case 'episodic': return 'magenta';
        case 'procedural': return 'green';
        case 'preference': return 'white';
        case 'evidence': return 'green';
        default: return 'gray';
    }
}

import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text } from 'ink';
export const MemoryInspectView = ({ memoryItems }) => {
    const defaultItems = memoryItems || [
        {
            id: 'mem-01',
            tier: 'working',
            content: 'Paginator start index adjusted to (page - 1) * size',
            provenance: 'AST indexer + code edit step 3a',
            invalidationRule: 'Invalidate on paginator.py change',
            createdAt: '2026-08-07 12:45:00'
        },
        {
            id: 'mem-02',
            tier: 'project',
            content: 'Pytest configuration targets tests/ directory',
            provenance: 'repo_scanner: pytest.ini',
            createdAt: '2026-08-07 12:40:00'
        }
    ];
    return (_jsxs(Box, { flexDirection: "column", padding: 1, minHeight: 12, children: [_jsx(Text, { color: "cyan", bold: true, children: "Tiered Memory Inspection Browser (7 Tiers)" }), _jsx(Box, { flexDirection: "column", marginY: 1, children: defaultItems.map((item) => (_jsxs(Box, { flexDirection: "column", borderStyle: "single", borderColor: "gray", paddingX: 1, marginY: 1, children: [_jsxs(Box, { justifyContent: "space-between", children: [_jsxs(Text, { color: "magenta", bold: true, children: ["[", item.tier.toUpperCase(), "] ", item.id] }), _jsx(Text, { color: "gray", children: item.createdAt })] }), _jsx(Text, { color: "white", children: item.content }), _jsxs(Text, { color: "yellow", children: ["Provenance: ", item.provenance] }), item.invalidationRule && (_jsxs(Text, { color: "red", dimColor: true, children: ["Rule: ", item.invalidationRule] }))] }, item.id))) })] }));
};

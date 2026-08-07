import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text } from 'ink';
import Spinner from 'ink-spinner';
import { SYMBOLS } from '../../utils/ansi.js';
export const IntakeView = ({ steps, ready }) => {
    const defaultSteps = steps && steps.length > 0 ? steps : [
        { id: '1', step: 'Scanning repository workspace', completed: true, detail: '1,204 files indexed' },
        { id: '2', step: 'Building symbol graph', completed: true, detail: '8,431 symbols' },
        { id: '3', step: 'Building test-to-source map', completed: true, detail: '312 test files' },
        { id: '4', step: 'Loading git history', completed: true, detail: '2,140 commits' },
    ];
    return (_jsxs(Box, { flexDirection: "column", padding: 1, minHeight: 12, children: [_jsx(Text, { bold: true, color: "cyan", children: "Scanning repository workspace\u2026" }), _jsx(Box, { flexDirection: "column", marginY: 1, gap: 1, children: defaultSteps.map((item) => (_jsxs(Box, { gap: 1, children: [item.completed ? (_jsx(Text, { color: "green", children: SYMBOLS.DONE })) : item.running ? (_jsx(Text, { color: "yellow", children: _jsx(Spinner, { type: "dots" }) })) : (_jsx(Text, { color: "gray", children: SYMBOLS.PENDING })), _jsx(Text, { color: item.completed ? 'white' : item.running ? 'yellow' : 'gray', bold: item.running, children: item.step }), item.detail && _jsxs(Text, { color: "gray", children: ["(", item.detail, ")"] })] }, item.id))) }), ready ? (_jsxs(Box, { marginTop: 1, flexDirection: "column", borderStyle: "single", borderColor: "green", paddingX: 1, children: [_jsx(Text, { color: "green", bold: true, children: "\u2713 Ready. Describe the issue or feature you'd like addressed:" }), _jsx(Text, { color: "gray", children: "Type prompt below (e.g., \"Fix off-by-one error in pagination\") and press Enter." })] })) : (_jsx(Box, { marginTop: 1, children: _jsxs(Text, { color: "yellow", children: [_jsx(Spinner, { type: "dots" }), " ", _jsx(Text, { color: "yellow", children: "Indexing repository structure..." })] }) }))] }));
};

import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text } from 'ink';
import Spinner from 'ink-spinner';
import { SYMBOLS } from '../../utils/ansi.js';
export const TraceView = ({ verifications, logs, recoveringReason, isVerificationRunning = false }) => {
    const defaultSuites = verifications && verifications.length > 0 ? verifications : [
        { name: 'build', status: 'passed', durationSeconds: 3.2 },
        { name: 'lint', status: 'passed', durationSeconds: 0.8 },
        { name: 'type check', status: 'passed', durationSeconds: 1.1 },
        { name: 'unit tests (312)', status: 'passed', durationSeconds: 11.4 },
        {
            name: 'regression tests (18)',
            status: 'failed',
            durationSeconds: 4.7,
            errorReason: 'test_pagination_last_page AssertionError'
        }
    ];
    return (_jsxs(Box, { flexDirection: "column", padding: 1, minHeight: 12, children: [_jsxs(Box, { gap: 1, marginBottom: 1, children: [_jsx(Text, { color: "cyan", bold: true, children: "Running verification suite\u2026" }), isVerificationRunning && (_jsx(Text, { color: "yellow", children: _jsx(Spinner, { type: "dots" }) }))] }), _jsx(Box, { flexDirection: "column", marginY: 1, children: defaultSuites.map((item, idx) => (_jsxs(Box, { flexDirection: "column", children: [_jsxs(Box, { gap: 1, children: [_jsxs(Text, { color: "white", children: ["  ", item.name] }), _jsx(Text, { color: "gray", children: "............................." }), item.status === 'passed' ? (_jsxs(Text, { color: "green", children: [SYMBOLS.DONE, " passed (", item.durationSeconds, "s)"] })) : item.status === 'running' ? (_jsxs(Text, { color: "yellow", children: [_jsx(Spinner, { type: "dots" }), " running..."] })) : item.status === 'failed' ? (_jsxs(Text, { color: "red", children: [SYMBOLS.FAILED, " 1 failed (", item.durationSeconds, "s)"] })) : (_jsxs(Text, { color: "gray", children: [SYMBOLS.PENDING, " pending"] }))] }), item.errorReason && (_jsx(Box, { marginX: 4, children: _jsxs(Text, { color: "red", children: ["\u2514\u2500 ", item.errorReason] }) }))] }, idx))) }), recoveringReason ? (_jsxs(Box, { marginTop: 1, padding: 1, borderStyle: "single", borderColor: "yellow", flexDirection: "column", children: [_jsxs(Text, { color: "yellow", bold: true, children: ["Recovering: ", recoveringReason] }), _jsx(Text, { color: "gray", dimColor: true, children: "Re-inspecting failing test \u2192 drafting patch \u2192 re-running verification suite" })] })) : (_jsxs(Box, { marginTop: 1, paddingX: 1, borderStyle: "single", borderColor: "gray", children: [_jsx(Text, { color: "gray", children: "Status: " }), _jsx(Text, { color: "green", children: "All automated verification gates active." })] })), logs && logs.length > 0 && (_jsxs(Box, { marginTop: 1, flexDirection: "column", borderStyle: "single", borderColor: "gray", paddingX: 1, children: [_jsxs(Text, { color: "gray", bold: true, children: ["Live Execution Log Stream (last ", Math.min(logs.length, 5), " events):"] }), logs.slice(-5).map((logLine, i) => (_jsx(Text, { color: "gray", dimColor: true, children: logLine }, i)))] })), _jsxs(Box, { marginTop: 1, gap: 3, children: [_jsx(Text, { color: "gray", children: "Tab: switch view" }), _jsx(Text, { color: "magenta", children: "/plan: task graph" }), _jsx(Text, { color: "magenta", children: "/summary: reviewer summary" })] })] }));
};

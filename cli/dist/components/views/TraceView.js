import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text } from 'ink';
import { SYMBOLS } from '../../utils/ansi.js';
export const TraceView = ({ verifications, logs, recoveringReason }) => {
    const defaultSuites = verifications || [
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
    return (_jsxs(Box, { flexDirection: "column", padding: 1, minHeight: 12, children: [_jsx(Text, { color: "cyan", bold: true, children: "Running verification suite..." }), _jsx(Box, { flexDirection: "column", marginY: 1, children: defaultSuites.map((item, idx) => (_jsxs(Box, { flexDirection: "column", children: [_jsxs(Box, { gap: 1, children: [_jsxs(Text, { color: "white", children: ["  ", item.name] }), _jsx(Text, { color: "gray", children: "............................." }), _jsxs(Text, { color: item.status === 'passed' ? 'green' : 'red', children: [item.status === 'passed' ? SYMBOLS.DONE : SYMBOLS.FAILED, ' ', item.status, " (", item.durationSeconds, "s)"] })] }), item.errorReason && (_jsx(Box, { marginX: 4, children: _jsxs(Text, { color: "red", children: ["\u2514\u2500 ", item.errorReason] }) }))] }, idx))) }), recoveringReason && (_jsx(Box, { marginTop: 1, padding: 1, borderStyle: "single", borderColor: "yellow", children: _jsxs(Text, { color: "yellow", bold: true, children: ["Recovering: ", recoveringReason] }) })), logs && logs.length > 0 && (_jsxs(Box, { marginTop: 1, flexDirection: "column", children: [_jsx(Text, { color: "gray", bold: true, children: "Execution Logs:" }), logs.slice(-5).map((log, i) => (_jsx(Text, { color: "gray", dimColor: true, children: log }, i)))] }))] }));
};

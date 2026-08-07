import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text } from 'ink';
export const StatusStrip = ({ session, currentTaskLabel }) => {
    const formatTime = (secs) => {
        const m = Math.floor(secs / 60);
        const s = secs % 60;
        return `${m}m ${s}s`;
    };
    return (_jsxs(Box, { borderStyle: "single", borderColor: "gray", paddingX: 1, justifyContent: "space-between", children: [_jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "yellow", bold: true, children: "\uD83D\uDC51 ROYAL HARNESS" }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "gray", children: ["Stage: ", _jsx(Text, { color: "white", bold: true, children: currentTaskLabel || 'Autonomous Agent Execution' })] })] }), _jsxs(Box, { gap: 2, children: [_jsxs(Text, { color: "gray", children: ["Tests: ", _jsx(Text, { color: "green", bold: true, children: session.testsPassing || '5/5 Passed' })] }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "gray", children: ["Elapsed: ", _jsx(Text, { color: "cyan", children: formatTime(session.elapsedSeconds || 0) })] }), _jsx(Text, { color: "gray", children: "|" }), _jsx(Text, { color: "magenta", bold: true, children: "[Tab] Switch View" })] })] }));
};

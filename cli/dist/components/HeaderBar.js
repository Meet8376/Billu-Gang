import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text } from 'ink';
import { formatElapsedTime } from '../utils/formatters.js';
export const HeaderBar = ({ session, activeView }) => {
    return (_jsxs(Box, { borderStyle: "single", borderColor: "blue", paddingX: 1, justifyContent: "space-between", children: [_jsxs(Box, { gap: 1, children: [_jsx(Text, { color: "blue", bold: true, children: "AE-01 HARNESS" }), _jsx(Text, { color: "gray", children: "|" }), _jsx(Text, { color: "cyan", bold: true, children: session.repoName }), _jsxs(Text, { color: "gray", children: ["(", session.branch, ")"] })] }), _jsxs(Box, { gap: 2, children: [_jsxs(Text, { color: "magenta", children: ["Model: ", session.modelProvider] }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "yellow", children: ["ID: ", session.sessionId] }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "green", children: ["Time: ", formatElapsedTime(session.elapsedSeconds)] }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "white", bold: true, children: ["VIEW: [", activeView.toUpperCase(), "]"] })] })] }));
};

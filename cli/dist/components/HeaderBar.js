import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text } from 'ink';

export const HeaderBar = ({ session, activeView }) => {
    const algoBal = session.algoBalance ?? 0;
    return (_jsxs(Box, { flexDirection: "column", borderStyle: "round", borderColor: "yellow", paddingX: 1, marginY: 0, flexShrink: 0, children: [_jsxs(Box, { justifyContent: "space-between", alignItems: "center", children: [_jsx(Text, { color: "yellow", bold: true, children: "BILLU GANG  |  AGENTIC HARNESS" }), _jsxs(Text, { color: "magenta", bold: true, children: ["[", session.modelProvider || 'gemini-3.5-flash-lite', "]"] })] }), _jsxs(Box, { gap: 1, marginTop: 0, flexWrap: "wrap", children: [_jsxs(Text, { color: "gray", children: ["Repo: ", _jsx(Text, { color: "white", bold: true, children: session.repoName })] }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "gray", children: ["Tier: ", session.tier === 'algo' ? (algoBal > 0 ? (_jsxs(Text, { color: "yellow", bold: true, children: ["[ALGO: ", algoBal, " ALGO ($", (algoBal * 0.2).toFixed(2), ")]"] })) : (_jsx(Text, { color: "red", bold: true, children: "[ALGO: UNPAID (0.0 ALGO)]" }))) : (_jsx(Text, { color: "cyan", bold: true, children: "[FREE TIER]" }))] }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "gray", children: ["Branch: ", _jsx(Text, { color: "cyan", children: session.branch || 'main' })] }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "gray", children: ["Sandbox: ", _jsxs(Text, { color: "green", bold: true, children: ["[", session.sandboxState?.toUpperCase() || 'ACTIVE', "]"] })] }), _jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "gray", children: ["View: ", _jsx(Text, { color: "yellow", bold: true, children: activeView === 'graph' ? 'Task Graph' : activeView === 'diff' ? 'Diff View' : 'SWE Benchmark' })] })] })] }));

};




import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text, useInput } from 'ink';
export const ApprovalPrompt = ({ commandToApprove, reason, onRespond }) => {
    useInput((input, key) => {
        if (input.toLowerCase() === 'y') {
            onRespond(true);
        }
        else if (input.toLowerCase() === 'n' || key.escape || key.return) {
            onRespond(false);
        }
    }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });
    return (_jsxs(Box, { flexDirection: "column", borderStyle: "double", borderColor: "red", padding: 1, margin: 1, children: [_jsx(Text, { color: "red", bold: true, children: "\u26A0\uFE0F SAFETY APPROVAL REQUIRED" }), _jsxs(Text, { color: "yellow", children: ["Reason: ", reason] }), _jsx(Box, { marginY: 1, paddingX: 1, borderStyle: "single", borderColor: "yellow", children: _jsx(Text, { color: "white", bold: true, children: commandToApprove }) }), _jsxs(Text, { color: "white", children: ["Allow harness to execute this command in sandbox? [", _jsx(Text, { color: "green", bold: true, children: "y" }), "/", _jsx(Text, { color: "red", bold: true, children: "N" }), "]:"] })] }));
};

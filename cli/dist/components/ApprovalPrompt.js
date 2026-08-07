import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text, useInput } from 'ink';
export const ApprovalPrompt = ({ request, commandToApprove, reason, onRespond }) => {
    const targetCommand = request ? request.command : commandToApprove || 'npm install package-outside-scope';
    const targetReason = request ? request.reason : reason || 'Accesses network outside sandbox allowlist';
    useInput((input, key) => {
        if (input.toLowerCase() === 'y') {
            onRespond(true);
        }
        else if (input.toLowerCase() === 'n' || key.escape || key.return) {
            onRespond(false);
        }
    }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });
    return (_jsxs(Box, { flexDirection: "column", borderStyle: "double", borderColor: "red", padding: 1, margin: 1, children: [_jsx(Text, { color: "red", bold: true, children: "\u26A0\uFE0F SAFETY APPROVAL REQUIRED \u2014 OUT-OF-SCOPE COMMAND" }), _jsxs(Box, { marginY: 1, children: [_jsx(Text, { color: "yellow", children: "Reason: " }), _jsx(Text, { color: "white", children: targetReason })] }), _jsxs(Box, { marginY: 1, paddingX: 1, borderStyle: "single", borderColor: "yellow", flexDirection: "column", children: [_jsx(Text, { color: "gray", children: "Proposed Command:" }), _jsx(Text, { color: "white", bold: true, children: targetCommand })] }), _jsxs(Box, { marginTop: 1, gap: 1, children: [_jsx(Text, { color: "white", children: "Allow harness to execute this command in sandbox? [" }), _jsx(Text, { color: "green", bold: true, underline: true, children: "y" }), _jsx(Text, { color: "white", children: "/" }), _jsx(Text, { color: "red", bold: true, underline: true, children: "N" }), _jsx(Text, { color: "white", children: "]:" })] }), _jsx(Box, { marginTop: 1, children: _jsx(Text, { color: "gray", dimColor: true, children: "Press 'y' to approve, or 'n' / Esc to block execution (Default: Deny)." }) })] }));
};

import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text, useInput } from 'ink';

export const ApprovalPrompt = ({ request, commandToApprove, reason, repoName, branch, onRespond }) => {
    const targetCommand = request?.command || commandToApprove || 'git push origin main';
    const targetReason = request?.reason || reason || 'Pushing verified commits & code patches to remote GitHub repository';
    const targetRepo = request?.repoName || repoName || 'Billu-Gang';
    const targetBranch = request?.branch || branch || 'main';
    useInput((input, key) => {
        if (input.toLowerCase() === 'y') {
            onRespond(true);
        }
        else if (input.toLowerCase() === 'n' || key.escape) {
            onRespond(false);
        }
    }, { isActive: true });
    return (_jsxs(Box, { flexDirection: "column", borderStyle: "round", borderColor: "yellow", paddingX: 2, paddingY: 1, margin: 1, children: [_jsx(Box, { justifyContent: "center", marginBottom: 1, children: _jsx(Text, { color: "yellow", bold: true, children: "SECURITY APPROVAL GATE - GIT COMMIT / PUSH" }) }), _jsxs(Box, { flexDirection: "column", borderStyle: "single", borderColor: "magenta", paddingX: 1, marginY: 1, children: [_jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "yellow", bold: true, children: "Repository :" }), _jsx(Text, { color: "white", bold: true, children: targetRepo })] }), _jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "yellow", bold: true, children: "Branch     :" }), _jsx(Text, { color: "cyan", children: targetBranch })] }), _jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "yellow", bold: true, children: "Command    :" }), _jsx(Text, { color: "green", bold: true, children: targetCommand })] }), _jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "yellow", bold: true, children: "Reason     :" }), _jsx(Text, { color: "white", children: targetReason })] })] }), _jsxs(Box, { marginY: 1, children: [_jsx(Text, { color: "yellow", bold: true, children: "SECURITY NOTICE:" }), _jsxs(Text, { color: "gray", children: [' ', "This action will write local codebase modifications directly to GitHub."] })] }), _jsxs(Box, { marginTop: 1, gap: 1, alignItems: "center", children: [_jsx(Text, { color: "white", bold: true, children: "Push code to GitHub? [" }), _jsx(Text, { color: "green", bold: true, underline: true, children: "y" }), _jsx(Text, { color: "white", children: "/" }), _jsx(Text, { color: "red", bold: true, underline: true, children: "N" }), _jsx(Text, { color: "white", bold: true, children: "]:" })] }), _jsx(Box, { marginTop: 1, children: _jsx(Text, { color: "gray", dimColor: true, children: "Press 'y' to confirm & push to GitHub | Press 'n' or Esc to cancel execution (Default: Deny)" }) })] }));
};


import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Box, Text } from 'ink';

export const HeaderBar = ({ session }) => {
    return (_jsxs(Box, {
        flexDirection: "column", borderStyle: "double", borderColor: "cyan", paddingX: 1, marginY: 0, children: [
            _jsx(Text, { color: "cyan", bold: true, children: "=========================================================" }),
            _jsx(Text, { color: "blue", bold: true, children: "Secure AI Code Review Sandbox" }),
            _jsx(Text, { color: "cyan", bold: true, children: "=========================================================" }),
            _jsxs(Box, {
                flexDirection: "column", marginY: 0, children: [
                    _jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "gray", children: "Repository :" }), _jsx(Text, { color: "white", bold: true, children: session.repoName })] }),
                    _jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "gray", children: "Branch     :" }), _jsx(Text, { color: "yellow", children: session.branch || 'main' })] }),
                    _jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "gray", children: "AI Model   :" }), _jsx(Text, { color: "magenta", bold: true, children: session.modelProvider })] }),
                    _jsxs(Box, { gap: 2, children: [_jsx(Text, { color: "gray", children: "Status     :" }), _jsx(Text, { color: "green", bold: true, children: `[${(session.sandboxState || 'RUNNING').toUpperCase()}]` })] })
                ]
            })
        ]
    }));
};

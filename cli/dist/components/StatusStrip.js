import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { Box, Text } from 'ink';

export const StatusStrip = ({ session, currentTaskLabel }) => {
    return (_jsxs(Box, {
        borderStyle: "single", borderColor: "gray", paddingX: 1, justifyContent: "space-between", children: [
            _jsxs(Box, {
                gap: 1, children: [
                    _jsx(Text, { color: "gray", children: "Sandbox Status:" }),
                    _jsx(Text, { color: "green", bold: true, children: `[${(session.sandboxState || 'ACTIVE').toUpperCase()}]` }),
                    currentTaskLabel && (_jsxs(_Fragment, { children: [_jsx(Text, { color: "gray", children: "|" }), _jsxs(Text, { color: "white", children: ["Stage: ", currentTaskLabel] })] }))
                ]
            }),
            _jsxs(Box, {
                gap: 2, children: [
                    _jsxs(Text, { color: "gray", children: ["Tests: ", _jsx(Text, { color: "cyan", bold: true, children: session.testsPassing || 'All Passed' })] }),
                    _jsx(Text, { color: "gray", children: "|" }),
                    _jsx(Text, { color: "magenta", children: "Tab: Switch View" })
                ]
            })
        ]
    }));
};

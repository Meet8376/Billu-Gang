import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import { Box, Text } from 'ink';
import { formatCurrency, formatTokenCount, formatElapsedTime } from '../../utils/formatters.js';
export const ReviewerSummaryView = ({ summary, onApplyPatch, onDiscardPatch }) => {
    const data = summary || {
        taskTitle: 'Fix off-by-one error in pagination',
        filesChangedCount: 2,
        testsPassingRatio: '330/330 passing',
        cost: 0.14,
        tokens: 42110,
        durationSeconds: 47,
        recoveryActionsCount: 1,
        completenessRationale: 'Off-by-one corrected in get_page(); regression test now passes.',
        uncertaintyNotes: 'None flagged — full suite green.',
        rollbackCommand: 'ae-harness rollback fix-pagination-01'
    };
    return (_jsxs(Box, { flexDirection: "column", padding: 1, minHeight: 12, children: [_jsxs(Text, { color: "green", bold: true, children: ["\u2713 Patch complete \u2014 \"", data.taskTitle, "\""] }), _jsxs(Box, { flexDirection: "column", marginY: 1, paddingX: 1, borderStyle: "single", borderColor: "gray", children: [_jsxs(Box, { gap: 6, children: [_jsxs(Text, { color: "gray", children: ["Files changed: ", _jsx(Text, { color: "white", bold: true, children: data.filesChangedCount })] }), _jsxs(Text, { color: "gray", children: ["Tests: ", _jsx(Text, { color: "green", bold: true, children: data.testsPassingRatio })] })] }), _jsxs(Box, { gap: 6, marginTop: 1, children: [_jsxs(Text, { color: "gray", children: ["Cost: ", _jsx(Text, { color: "green", bold: true, children: formatCurrency(data.cost) })] }), _jsxs(Text, { color: "gray", children: ["Tokens: ", _jsx(Text, { color: "white", bold: true, children: formatTokenCount(data.tokens) })] }), _jsxs(Text, { color: "gray", children: ["Duration: ", _jsx(Text, { color: "yellow", bold: true, children: formatElapsedTime(data.durationSeconds) })] }), _jsxs(Text, { color: "gray", children: ["Recovery actions: ", _jsx(Text, { color: "magenta", bold: true, children: data.recoveryActionsCount })] })] })] }), _jsxs(Box, { flexDirection: "column", marginTop: 1, children: [_jsx(Text, { color: "cyan", bold: true, children: "Why it's complete:" }), _jsxs(Text, { color: "white", children: ["  ", data.completenessRationale] })] }), _jsxs(Box, { flexDirection: "column", marginTop: 1, children: [_jsx(Text, { color: "yellow", bold: true, children: "Remaining uncertainty:" }), _jsxs(Text, { color: "white", children: ["  ", data.uncertaintyNotes] })] }), _jsxs(Box, { flexDirection: "column", marginTop: 1, children: [_jsx(Text, { color: "red", bold: true, children: "Rollback:" }), _jsxs(Text, { color: "gray", children: ["  ", data.rollbackCommand] })] }), _jsxs(Box, { marginTop: 1, gap: 3, children: [_jsx(Text, { color: "green", children: "\u23CE /apply: apply patch" }), _jsx(Text, { color: "red", children: "\u23CE /rollback: discard & rollback" }), _jsx(Text, { color: "magenta", children: "\u23CE /trace: view full trace" })] })] }));
};

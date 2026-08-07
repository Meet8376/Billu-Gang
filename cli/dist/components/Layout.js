import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Box, useInput } from 'ink';
import { HeaderBar } from './HeaderBar.js';
import { StatusStrip } from './StatusStrip.js';
import { CommandLine } from './CommandLine.js';
import { ApprovalPrompt } from './ApprovalPrompt.js';
import { IntakeView } from './views/IntakeView.js';
import { TaskGraphView } from './views/TaskGraphView.js';
import { DiffView } from './views/DiffView.js';
import { TraceView } from './views/TraceView.js';
import { ReviewerSummaryView } from './views/ReviewerSummaryView.js';
import { MemoryInspectView } from './views/MemoryInspectView.js';
import { BenchmarkView } from './views/BenchmarkView.js';
export const Layout = ({ session, onCommandSubmit, intakeSteps, intakeReady, taskTitle, taskNodes, activeViewOverride, diffFileFilter, pendingApproval, onApprovalResponse }) => {
    const [activeView, setActiveView] = useState('intake');
    // Allow external slash-command handler to override view state
    const currentView = activeViewOverride || activeView;
    // Keyboard navigation across view tabs using Tab key
    useInput((input, key) => {
        if (key.tab) {
            const views = ['intake', 'graph', 'diff', 'trace', 'summary', 'memory', 'benchmark'];
            const currentIndex = views.indexOf(currentView);
            const nextIndex = (currentIndex + 1) % views.length;
            setActiveView(views[nextIndex]);
        }
    }, { isActive: Boolean(process.stdin && process.stdin.isTTY) });
    const handleCommand = (cmd) => {
        const trimmed = cmd.toLowerCase().trim();
        if (trimmed.startsWith('/plan') || trimmed.startsWith('/graph')) {
            setActiveView('graph');
        }
        else if (trimmed.startsWith('/diff')) {
            setActiveView('diff');
        }
        else if (trimmed.startsWith('/trace') || trimmed.startsWith('/logs')) {
            setActiveView('trace');
        }
        else if (trimmed.startsWith('/summary') || trimmed.startsWith('/review')) {
            setActiveView('summary');
        }
        else if (trimmed.startsWith('/memory')) {
            setActiveView('memory');
        }
        else if (trimmed.startsWith('/benchmark') || trimmed.startsWith('/eval')) {
            setActiveView('benchmark');
        }
        else if (trimmed.startsWith('/intake')) {
            setActiveView('intake');
        }
        onCommandSubmit(cmd);
    };
    const renderMainPane = () => {
        switch (currentView) {
            case 'intake':
                return _jsx(IntakeView, { steps: intakeSteps, ready: intakeReady });
            case 'graph':
                return _jsx(TaskGraphView, { taskTitle: taskTitle, nodes: taskNodes });
            case 'diff':
                return _jsx(DiffView, { activeFileFilter: diffFileFilter });
            case 'trace':
                return _jsx(TraceView, {});
            case 'summary':
                return _jsx(ReviewerSummaryView, {});
            case 'memory':
                return _jsx(MemoryInspectView, {});
            case 'benchmark':
                return _jsx(BenchmarkView, {});
            default:
                return _jsx(IntakeView, { steps: intakeSteps, ready: intakeReady });
        }
    };
    return (_jsxs(Box, { flexDirection: "column", width: "100%", height: "100%", children: [_jsx(HeaderBar, { session: session, activeView: currentView }), _jsx(Box, { flexGrow: 1, borderStyle: "single", borderColor: "blue", flexDirection: "column", children: pendingApproval ? (_jsx(ApprovalPrompt, { commandToApprove: pendingApproval.command, reason: pendingApproval.reason, onRespond: onApprovalResponse || (() => { }) })) : (renderMainPane()) }), _jsx(StatusStrip, { session: session, currentTaskLabel: taskTitle }), _jsx(CommandLine, { onSubmit: handleCommand, disabled: Boolean(pendingApproval) })] }));
};

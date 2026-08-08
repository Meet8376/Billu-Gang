import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { Box, Text, useInput, useStdout } from 'ink';
import { HeaderBar } from './HeaderBar.js';
import { StatusStrip } from './StatusStrip.js';
import { CommandLine } from './CommandLine.js';
import { ApprovalPrompt } from './ApprovalPrompt.js';
import { TaskGraphView } from './views/TaskGraphView.js';
import { DiffView } from './views/DiffView.js';
import { BenchmarkView } from './views/BenchmarkView.js';

export function useTerminalSize() {
    const { stdout } = useStdout();
    const [size, setSize] = useState({
        columns: stdout?.columns || process.stdout.columns || 80,
        rows: stdout?.rows || process.stdout.rows || 24
    });
    useEffect(() => {
        const handleResize = () => {
            const cols = stdout?.columns || process.stdout.columns || 80;
            const rws = stdout?.rows || process.stdout.rows || 24;
            setSize({ columns: cols, rows: rws });
        };
        handleResize();
        stdout?.on('resize', handleResize);
        process.stdout?.on('resize', handleResize);
        return () => {
            stdout?.off('resize', handleResize);
            process.stdout?.off('resize', handleResize);
        };
    }, [stdout]);
    return size;
}

export const Layout = ({ session, onCommandSubmit, taskTitle, taskNodes, activeViewOverride, onClearViewOverride, diffFileFilter, pendingApproval, onApprovalResponse }) => {
    const [activeView, setActiveView] = useState('graph');
    const { columns, rows } = useTerminalSize();

    useEffect(() => {
        if (activeViewOverride) {
            setActiveView(activeViewOverride);
            if (onClearViewOverride) {
                onClearViewOverride();
            }
        }
    }, [activeViewOverride]);

    const currentView = activeView;
    useInput((input, key) => {
        if (key.tab) {
            if (onClearViewOverride) onClearViewOverride();
            setActiveView((prev) => (prev === 'graph' ? 'diff' : prev === 'diff' ? 'benchmark' : 'graph'));
        }
    }, { isActive: true });

    const handleCommand = (cmd) => {
        const trimmed = cmd.toLowerCase().trim();
        if (trimmed.startsWith('/plan') || trimmed.startsWith('/graph') || trimmed.startsWith('/tasks')) {
            if (onClearViewOverride) onClearViewOverride();
            setActiveView('graph');
        }
        else if (trimmed.startsWith('/diff') || trimmed.startsWith('/patch')) {
            if (onClearViewOverride) onClearViewOverride();
            setActiveView('diff');
        }
        else if (trimmed.startsWith('/benchmark') || trimmed.startsWith('/eval') || trimmed.startsWith('/swe')) {
            if (onClearViewOverride) onClearViewOverride();
            setActiveView('benchmark');
        }
        onCommandSubmit(cmd);
    };

    // Calculate dynamic line bounds to eliminate flickering on shrinking terminals
    const availableContentRows = Math.max(1, rows - 11);
    const renderMainPane = () => {
        switch (currentView) {
            case 'graph':
                return (_jsx(TaskGraphView, { taskTitle: taskTitle, nodes: taskNodes, maxVisibleNodes: availableContentRows }));
            case 'diff':
                return (_jsx(DiffView, { activeFileFilter: diffFileFilter, maxDiffLines: availableContentRows, repoPath: session.repoName }));
            case 'benchmark':
                return (_jsx(BenchmarkView, { currentRepo: session.repoName, currentTaskPrompt: taskTitle, currentTestStatus: session.testsPassing }));

            default:
                return (_jsx(TaskGraphView, { taskTitle: taskTitle, nodes: taskNodes, maxVisibleNodes: availableContentRows }));
        }
    };
    return (_jsxs(Box, { flexDirection: "column", width: columns, height: rows, overflow: "hidden", children: [_jsx(HeaderBar, { session: session, activeView: currentView }), _jsxs(Box, { paddingX: 1, marginY: 0, gap: 2, flexShrink: 0, children: [_jsx(Box, { gap: 1, children: _jsxs(Text, { color: currentView === 'graph' ? 'yellow' : 'gray', bold: currentView === 'graph', underline: currentView === 'graph', children: ["[ Task Graph ", currentView === 'graph' ? '(Active)' : '', " ]"] }) }), _jsx(Box, { gap: 1, children: _jsxs(Text, { color: currentView === 'diff' ? 'yellow' : 'gray', bold: currentView === 'diff', underline: currentView === 'diff', children: ["[ Diff View ", currentView === 'diff' ? '(Active)' : '', " ]"] }) }), _jsx(Box, { gap: 1, children: _jsxs(Text, { color: currentView === 'benchmark' ? 'yellow' : 'gray', bold: currentView === 'benchmark', underline: currentView === 'benchmark', children: ["[ SWE Benchmark ", currentView === 'benchmark' ? '(Active)' : '', " ]"] }) })] }), _jsx(Box, { flexGrow: 1, borderStyle: "round", borderColor: currentView === 'graph' ? 'yellow' : 'cyan', flexDirection: "column", overflow: "hidden", children: pendingApproval ? (_jsx(ApprovalPrompt, { commandToApprove: pendingApproval.command, reason: pendingApproval.reason, repoName: session.repoName, branch: session.branch, onRespond: onApprovalResponse || (() => { }) })) : (renderMainPane()) }), _jsx(StatusStrip, { session: session, currentTaskLabel: taskTitle }), _jsx(CommandLine, { onSubmit: handleCommand, disabled: false })] }));
};




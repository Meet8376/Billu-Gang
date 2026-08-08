import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import { useState } from 'react';
import { Box, Text, useInput, useStdout } from 'ink';

export const CommandLine = ({ onSubmit, disabled = false }) => {
    const [input, setInput] = useState('');
    const { stdout } = useStdout();
    const columns = stdout?.columns || process.stdout.columns || 80;
    const maxInputLen = Math.max(10, columns - 15);
    const displayInput = input.length > maxInputLen
        ? '...' + input.slice(input.length - maxInputLen + 3)
        : input;

    useInput((char, key) => {
        if (disabled)
            return;
        if (key.return) {
            if (input.trim().length > 0) {
                onSubmit(input.trim());
                setInput('');
            }
        }
        else if (key.backspace || key.delete) {
            setInput((prev) => prev.slice(0, -1));
        }
        else if (char && !key.ctrl && !key.meta) {
            setInput((prev) => prev + char);
        }
    }, { isActive: true });

    return (_jsxs(Box, { paddingX: 1, borderStyle: "round", borderColor: "magenta", flexShrink: 0, overflow: "hidden", children: [_jsx(Text, { color: "yellow", bold: true, children: "PROMPT > " }), _jsx(Text, { color: "white", bold: true, wrap: "truncate", children: displayInput }), _jsx(Text, { color: "yellow", dimColor: true, children: "_" })] }));
};


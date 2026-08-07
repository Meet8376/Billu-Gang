import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import { useState } from 'react';
import { Box, Text, useInput } from 'ink';
export const CommandLine = ({ onSubmit, disabled = false }) => {
    const [input, setInput] = useState('');
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
    return (_jsxs(Box, { paddingX: 1, borderStyle: "round", borderColor: "magenta", children: [_jsxs(Text, { color: "yellow", bold: true, children: ["\uD83D\uDC51 ROYAL PROMPT >", ' '] }), _jsx(Text, { color: "white", bold: true, children: input }), _jsx(Text, { color: "yellow", dimColor: true, children: "_" })] }));
};

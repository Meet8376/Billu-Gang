import React from 'react';
interface CommandLineProps {
    onSubmit: (command: string) => void;
    disabled?: boolean;
}
export declare const CommandLine: React.FC<CommandLineProps>;
export {};

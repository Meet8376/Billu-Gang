import React from 'react';
export interface AppProps {
    initialRepoPath: string;
    initialModel: string;
    useMockStream?: boolean;
}
export declare const AppContainer: React.FC<AppProps>;
export declare function runRepl(repoPath?: string, model?: string): void;

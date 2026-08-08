export async function handleSlashCommand(cmd, sessionId, apiClient) {
    switch (cmd.type) {
        case 'plan':
            return {
                handledLocally: true,
                activeViewTarget: 'graph',
                feedbackMessage: 'Switched to Task Graph View.'
            };
        case 'diff':
            return {
                handledLocally: true,
                activeViewTarget: 'diff',
                fileFilter: cmd.filterArg,
                feedbackMessage: cmd.filterArg
                    ? `Switched to Diff View (filter: ${cmd.filterArg}).`
                    : 'Switched to Diff View.'
            };
        case 'benchmark':
            return {
                handledLocally: true,
                activeViewTarget: 'benchmark',
                feedbackMessage: 'Switched to SWE Benchmark View.'
            };
        case 'approve':
            return {
                handledLocally: true,
                feedbackMessage: 'GitHub push approval requested.'
            };
        case 'help':
            return {
                handledLocally: true,
                feedbackMessage: 'Available commands: /graph, /plan, /diff [file], /benchmark, /approve, /push, /help'
            };
        default:
            return {
                handledLocally: false,
                feedbackMessage: `Unrecognized command: ${cmd.rawInput}`
            };
    }
}


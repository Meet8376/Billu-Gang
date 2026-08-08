export class SlashCommandRouter {
    static parse(input) {
        const trimmed = input.trim();
        if (!trimmed.startsWith('/')) {
            return { type: 'unknown', rawInput: input, commandName: '', args: [input] };
        }
        const parts = trimmed.slice(1).split(/\s+/);
        const commandName = parts[0].toLowerCase();
        const args = parts.slice(1);
        const filterArg = args[0];
        switch (commandName) {
            case 'plan':
            case 'graph':
            case 'tasks':
                return { type: 'plan', rawInput: input, commandName, args, filterArg };
            case 'diff':
            case 'patch':
                return { type: 'diff', rawInput: input, commandName, args, filterArg };
            case 'approve':
            case 'push':
            case 'yes':
            case 'y':
                return { type: 'approve', rawInput: input, commandName, args, filterArg };
            case 'help':
                return { type: 'help', rawInput: input, commandName, args, filterArg };
            default:
                return { type: 'unknown', rawInput: input, commandName, args, filterArg };
        }
    }
    static getSuggestions(input) {
        if (!input.startsWith('/'))
            return [];
        const prefix = input.toLowerCase();
        const available = ['/plan', '/graph', '/diff', '/patch', '/approve', '/push', '/help'];
        return available.filter((cmd) => cmd.startsWith(prefix));
    }
}

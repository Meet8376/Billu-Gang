/**
 * Utility functions for formatting currency, token counts, durations, and file paths.
 */
export function formatCurrency(amount) {
    return `$${amount.toFixed(2)}`;
}
export function formatTokenCount(tokens) {
    if (tokens >= 1_000_000) {
        return `${(tokens / 1_000_000).toFixed(2)}M`;
    }
    if (tokens >= 1_000) {
        return `${(tokens / 1_000).toFixed(1)}k`;
    }
    return tokens.toString();
}
export function formatElapsedTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    if (mins === 0) {
        return `${secs}s`;
    }
    return `${mins}m ${secs}s`;
}
export function formatTruncatedPath(path, maxLength = 30) {
    if (path.length <= maxLength)
        return path;
    return '...' + path.slice(-maxLength + 3);
}

/**
 * Utility functions for formatting currency, token counts, durations, and file paths.
 */

export function formatCurrency(amount: number): string {
  return `$${amount.toFixed(2)}`;
}

export function formatTokenCount(tokens: number): string {
  if (tokens >= 1_000_000) {
    return `${(tokens / 1_000_000).toFixed(2)}M`;
  }
  if (tokens >= 1_000) {
    return `${(tokens / 1_000).toFixed(1)}k`;
  }
  return tokens.toString();
}

export function formatElapsedTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  if (mins === 0) {
    return `${secs}s`;
  }
  return `${mins}m ${secs}s`;
}

export function formatTruncatedPath(path: string, maxLength: number = 30): string {
  if (path.length <= maxLength) return path;
  return '...' + path.slice(-maxLength + 3);
}

export function parseRepoName(repoPath: string): string {
  if (!repoPath) return 'Billu-Gang';
  let cleaned = repoPath.trim().replace(/[\/\\]+$/, '');
  if (cleaned.endsWith('.git')) {
    cleaned = cleaned.slice(0, -4);
  }
  const segments = cleaned.split(/[\/\\]/);
  const last = segments[segments.length - 1];
  return last || 'Billu-Gang';
}

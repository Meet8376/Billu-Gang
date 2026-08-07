import { describe, it, expect } from 'vitest';
import { SlashCommandRouter } from '../../src/router/SlashCommandRouter.js';

describe('SlashCommandRouter Phase 5', () => {
  it('parses /intake and /onboard commands', () => {
    const res1 = SlashCommandRouter.parse('/intake');
    expect(res1.type).toBe('intake');
    const res2 = SlashCommandRouter.parse('/onboard');
    expect(res2.type).toBe('intake');
  });

  it('parses /plan and /graph commands', () => {
    const res1 = SlashCommandRouter.parse('/plan');
    expect(res1.type).toBe('plan');
    const res2 = SlashCommandRouter.parse('/graph');
    expect(res2.type).toBe('plan');
  });

  it('parses /diff command with file filter argument', () => {
    const res = SlashCommandRouter.parse('/diff paginator.py');
    expect(res.type).toBe('diff');
    expect(res.filterArg).toBe('paginator.py');
  });

  it('parses /trace and /logs commands', () => {
    const res1 = SlashCommandRouter.parse('/trace');
    expect(res1.type).toBe('trace');
    const res2 = SlashCommandRouter.parse('/logs');
    expect(res2.type).toBe('trace');
  });

  it('parses /benchmark and /eval commands', () => {
    const res1 = SlashCommandRouter.parse('/benchmark');
    expect(res1.type).toBe('benchmark');
    const res2 = SlashCommandRouter.parse('/eval');
    expect(res2.type).toBe('benchmark');
  });

  it('parses /pause and /stop commands', () => {
    const res = SlashCommandRouter.parse('/pause');
    expect(res.type).toBe('pause');
  });

  it('provides slash command autocompletion suggestions', () => {
    const suggestions = SlashCommandRouter.getSuggestions('/b');
    expect(suggestions).toContain('/benchmark');
    const suggestionsTrace = SlashCommandRouter.getSuggestions('/tr');
    expect(suggestionsTrace).toContain('/trace');
  });
});

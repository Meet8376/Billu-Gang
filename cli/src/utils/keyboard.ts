/**
 * Keyboard action constants and hotkey helper definition for CLI navigation.
 */

export type KeyViewAction = 
  | 'SWITCH_INTAKE'
  | 'SWITCH_GRAPH'
  | 'SWITCH_DIFF'
  | 'SWITCH_TRACE'
  | 'SWITCH_SUMMARY'
  | 'SWITCH_MEMORY'
  | 'TOGGLE_HELP'
  | 'PAUSE';

export interface HotkeyGuide {
  key: string;
  description: string;
}

export const HOTKEYS: HotkeyGuide[] = [
  { key: 'Tab', description: 'Switch Active View' },
  { key: 'Esc', description: 'Pause Session' },
  { key: '/plan', description: 'Task Graph' },
  { key: '/diff', description: 'Unified Diff' },
  { key: '/trace', description: 'Live Trace Log' },
  { key: '/memory', description: 'Memory Inspection' },
  { key: '/rollback', description: 'Rollback Workspace' },
];

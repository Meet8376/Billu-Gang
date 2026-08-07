/**
 * Keyboard action constants and hotkey helper definition for CLI navigation.
 */
export type KeyViewAction = 'SWITCH_INTAKE' | 'SWITCH_GRAPH' | 'SWITCH_DIFF' | 'SWITCH_TRACE' | 'SWITCH_SUMMARY' | 'SWITCH_MEMORY' | 'TOGGLE_HELP' | 'PAUSE';
export interface HotkeyGuide {
    key: string;
    description: string;
}
export declare const HOTKEYS: HotkeyGuide[];

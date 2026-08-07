# AE-01 — Terminal CLI Frontend
### Visual & Layout Specification

---

## Overview

The frontend is a terminal UI (TUI) built with **Ink** (React for the terminal). It runs as a full-screen interactive session inside the user's terminal emulator, divided into fixed panes that update live as the backend streams plan revisions, tool calls, and test output over SSE. Below is a description of what each screen looks like and how it behaves.

---

## Layout Structure

The screen is divided into four persistent regions:

```
┌──────────────────────────────────────────────────────────────────┐
│  HEADER BAR                                                       │
│  repo name · branch · model · session id · elapsed time           │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  MAIN PANE                                                        │
│  (Plan / Task Graph / Diff / Trace — switches by active view)     │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  STATUS STRIP                                                     │
│  tokens used · cost so far · tests passing · sandbox state        │
├──────────────────────────────────────────────────────────────────┤
│  COMMAND / INPUT LINE                                             │
│  > _                                                               │
└──────────────────────────────────────────────────────────────────┘
```

- **Header bar** — always visible, one line, dark background, accent-colored text.
- **Main pane** — the largest region; content depends on the active view (see below).
- **Status strip** — thin, single-line, updates in real time as work happens.
- **Command line** — where the user types requests, approves actions, or issues slash-commands (`/plan`, `/diff`, `/trace`, `/rollback`).

---

## Views Inside the Main Pane

### 1. Repository Intake View
Shown right after `harness init`.

```
Scanning repository…
  ✓ 1,204 files indexed
  ✓ symbol graph built (8,431 symbols)
  ✓ test-to-source map built (312 test files)
  ✓ git history loaded (2,140 commits)

Ready. Describe the issue or feature you'd like addressed:
> _
```

Progress lines appear one at a time with a checkmark once each step completes; a spinner is shown next to the step currently running.

### 2. Task Graph View
Triggered automatically once a request is submitted.

```
Task Graph — "Fix off-by-one error in pagination"

  [1] Reproduce issue ..................... ✓ done
  [2] Locate relevant source ............... ✓ done
  [3] Draft patch .......................... ● running
       ├─ [3a] Modify paginator.py .......... ● running
       └─ [3b] Update tests ................. ○ pending
  [4] Run verification suite ............... ○ pending
  [5] Reviewer summary ...................... ○ pending

  ⏎ view diff   ⏎ view trace   ⏎ pause
```

Nodes are indented to show parallel branches. Status icons: `✓` done, `●` running (animated), `○` pending, `✗` failed/needs recovery.

### 3. Diff View
Shown when the user selects "view diff" or types `/diff`.

```
paginator.py                                          +4 −2
──────────────────────────────────────────────────────────
  42   def get_page(items, page, size):
  43 -     start = page * size
  44 -     end = start + size
  43 +     start = (page - 1) * size
  44 +     end = start + size
  45       return items[start:end]
```

Standard unified diff coloring: removed lines dimmed with a minus, added lines highlighted with a plus, line numbers in a muted column on the left.

### 4. Verification / Trace View
Shown while tests run or when the user types `/trace`.

```
Running verification suite…

  build ............................. ✓ passed (3.2s)
  lint ............................... ✓ passed (0.8s)
  type check .......................... ✓ passed (1.1s)
  unit tests (312) .................... ✓ 312 passed (11.4s)
  regression tests (18) ............... ✗ 1 failed  (4.7s)
       └─ test_pagination_last_page ..... AssertionError

  Recovering: re-inspecting failing test → patching → re-running
```

Failures are shown in a warning color with the failing test name and a one-line reason; recovery actions appear below as they happen, not as hidden reasoning.

### 5. Reviewer Summary View
Final screen at the end of a run.

```
✓ Patch complete — "Fix off-by-one error in pagination"

  Files changed: 2        Tests: 330/330 passing
  Cost: $0.14             Tokens: 42,110
  Duration: 47s           Recovery actions: 1

  Why it's complete:
    Off-by-one corrected in get_page(); regression test now passes.

  Remaining uncertainty:
    None flagged — full suite green.

  Rollback:
    harness rollback fix-pagination-01

  ⏎ apply patch   ⏎ discard   ⏎ view full trace
```

---

## Color & Style Conventions

| Element | Style |
|---|---|
| Header bar | Dark background, bold accent-blue text |
| Passed / done | Green checkmark, default text |
| Running | Yellow/animated dot, default text |
| Pending | Gray circle, dimmed text |
| Failed / needs attention | Red ✗, bold text |
| Diff additions | Green `+` prefix |
| Diff removals | Red `−` prefix, dimmed |
| Command line prompt | `>` in accent color, cursor blinking |
| Cost/token counters | Muted gray, right-aligned in status strip |

No colors are used to hide information — every state shown on screen corresponds to a real event streamed from the backend (plan step, tool call, test result), never to model-internal reasoning.

---

## Interaction Model

- **Keyboard-driven**: arrow keys move between task-graph nodes, `Enter` expands a node's detail, `Esc` returns to the previous view.
- **Slash-commands**: `/plan`, `/diff`, `/trace`, `/memory`, `/rollback`, `/approve`, `/pause`.
- **Approval gates**: any sandboxed command touching the filesystem outside the scoped workspace pauses execution and shows an inline approval prompt (`y/n`) before continuing.
- **Streaming**: all panes update incrementally as SSE events arrive — nothing waits for the full run to finish before showing progress.

---

*This spec describes the intended look and feel of the terminal frontend; implementation lives in the Ink-based CLI package described in the tech stack document.*

# Member 1 — Terminal CLI & TUI Lead: Directory Structure & File Specification

## 1. Overview & Ownership Domain
- **Member:** Member 1
- **Primary Role:** Terminal CLI & TUI Lead
- **Engineering Surfaces Owned:** User Interface, Interactive REPL, Approval Prompts, Live Event Rendering
- **Tech Stack & Tools:** Node.js, TypeScript, Ink (React-based TUI), Commander.js, Vitest, Zod, `eventsource` / native SSE
- **Primary Root Location:** `cli/`

---

## 2. Dedicated Directory Tree

```
cli/
├── package.json                        # Node.js dependencies & npm scripts (dev, build, test)
├── tsconfig.json                       # TypeScript compiler options
├── vitest.config.ts                    # Vitest configuration for TUI & component testing
├── README.md                           # CLI quickstart, slash-commands, and dev guidelines
│
├── src/
│   ├── index.ts                        # Executable CLI entrypoint (Commander.js program setup)
│   ├── cli.ts                          # CLI REPL loop runner & terminal environment initialization
│   │
│   ├── components/                     # Ink (React for Terminal) UI Components
│   │   ├── Layout.tsx                  # Base grid container (Header, Main Pane, Status Strip, Input)
│   │   ├── HeaderBar.tsx               # Top status bar (Session ID, Model Name, Cost $, Memory Tier)
│   │   ├── StatusStrip.tsx             # Bottom bar (Hotkeys, Connection status, Current active task)
│   │   ├── CommandLine.tsx             # Interactive prompt line with slash-command autocompletion
│   │   ├── ApprovalPrompt.tsx          # Safety confirmation dialog for out-of-scope commands [y/N]
│   │   │
│   │   └── views/                      # Main Pane Display Views (5 Core View States)
│   │       ├── IntakeView.tsx          # Repository intake & AST symbol scanning progress spinner
│   │       ├── TaskGraphView.tsx       # Interactive tree/DAG task graph with status icons (✓ ● ○ ✗)
│   │       ├── DiffView.tsx            # Syntax-highlighted unified patch diff viewer (+ green / - red)
│   │       ├── TraceView.tsx           # Live test streaming execution log & OpenTelemetry event log
│   │       ├── ReviewerSummaryView.tsx # Patch completion proof, cost breakdown & rollback instructions
│   │       └── MemoryInspectView.tsx   # Interactive /memory tier inspection, edit & export view
│   │
│   ├── router/
│   │   ├── SlashCommandRouter.ts       # Command dispatcher (/plan, /diff, /trace, /memory, /rollback)
│   │   └── commandHandlers.ts          # Individual slash-command logic & backend REST triggers
│   │
│   ├── sse/
│   │   ├── SSEClient.ts                # EventSource SSE streaming client connected to FastAPI
│   │   ├── sseTypes.ts                 # Zod schema definitions for incoming SSE event payloads
│   │   └── sseStreamHandler.ts         # Reactive state updates triggered by SSE events
│   │
│   ├── api/
│   │   ├── BackendApiClient.ts         # Axios/Fetch HTTP client for FastAPI REST endpoints
│   │   └── apiTypes.ts                 # TypeScript interfaces matching backend Pydantic models
│   │
│   └── utils/
│       ├── formatters.ts               # Currency ($), token count (k), and duration formatting
│       ├── ansi.ts                     # ANSI color codes, box drawing characters & visual spinners
│       └── keyboard.ts                 # Keyboard shortcuts listener (Tab, Arrow keys, Ctrl+C, Esc)
│
└── tests/
    ├── components/                     # Ink Component Render & Snapshot Tests
    │   ├── HeaderBar.test.tsx
    │   ├── TaskGraphView.test.tsx
    │   ├── DiffView.test.tsx
    │   └── ApprovalPrompt.test.tsx
    ├── router/
    │   └── SlashCommandRouter.test.ts  # Slash command parsing & routing unit tests
    └── sse/
        └── SSEClient.test.ts           # Mock SSE stream listener & event dispatcher tests
```

---

## 3. Detailed File Responsibilities & Key Exports

| File Path | Purpose & Responsibilities | Key Functions / Classes / Components |
|---|---|---|
| `src/index.ts` | Commander.js CLI initialization, command line flag parsing (`--model`, `--repo`). | `main()`, `program.parse()` |
| `src/cli.ts` | Terminal lifecycle initialization, Ink screen mount/unmount handler. | `runRepl()`, `initTerminal()` |
| `src/components/Layout.tsx` | Full-screen Ink container enforcing header, main pane, status strip, and input. | `<Layout />` |
| `src/components/HeaderBar.tsx` | Renders session metadata, model provider name, running token cost, and active memory tier. | `<HeaderBar session={...} />` |
| `src/components/StatusStrip.tsx` | Dynamic footer showing connection status, active hotkeys (`Tab`: switch view, `Esc`: pause). | `<StatusStrip connectionStatus={...} />` |
| `src/components/CommandLine.tsx` | Prompt input line with history buffer, slash-command suggestion popover. | `<CommandLine onSubmit={...} />` |
| `src/components/ApprovalPrompt.tsx` | Popup prompt requiring explicit `y` or `n` keypress for unapproved bash commands. | `<ApprovalPrompt request={...} onRespond={...} />` |
| `src/components/views/IntakeView.tsx` | Displays file scanning progress, tree-sitter AST symbol indexing status, git log intake. | `<IntakeView status={...} />` |
| `src/components/views/TaskGraphView.tsx` | Renders task graph DAG tree with animated spinners (`●`), success (`✓`), and fail (`✗`). | `<TaskGraphView nodes={...} selectedId={...} />` |
| `src/components/views/DiffView.tsx` | Renders colorized unified git diff patches produced by model edits. | `<DiffView patch={...} fileFilter={...} />` |
| `src/components/views/TraceView.tsx` | Renders live pytest output, build output logs, and raw event traces stream. | `<TraceView logs={...} autoScroll={true} />` |
| `src/components/views/ReviewerSummaryView.tsx` | Final completion report view: test proof, total cost, remaining uncertainties, rollback instructions. | `<ReviewerSummaryView summary={...} />` |
| `src/components/views/MemoryInspectView.tsx` | Visual memory browser for 7 tiers (working, task, project, etc.) with provenance info. | `<MemoryInspectView memoryItems={...} />` |
| `src/router/SlashCommandRouter.ts` | Parses user text for commands like `/plan`, `/diff`, `/trace`, `/memory`, `/rollback`. | `SlashCommandRouter.execute(input)` |
| `src/sse/SSEClient.ts` | Manages persistent EventSource connection to backend `GET /events` streaming endpoint. | `class SSEClient` (`connect()`, `onMessage()`) |
| `src/sse/sseTypes.ts` | Zod runtime schema validators for `plan_updated`, `tool_started`, `verification_finished` events. | `PlanUpdatedSchema`, `ToolStartedSchema` |
| `src/api/BackendApiClient.ts` | HTTP REST client methods targeting FastAPI endpoints (`/session`, `/plan`, `/run`, `/rollback`). | `class BackendApiClient` |

---

## 4. 24-Hour Phase Deliverables Schedule

```
Phase 1 (H0-H3) ──► Phase 2 (H3-H8) ──► Phase 3 (H8-H13) ──► Phase 4 (H13-H17) ──► Phase 5 (H17-H21) ──► Phase 6 (H21-H24)
  Boilerplate &       Core Ink Views       Backend SSE Link       Approval Prompt &     Visual Polish &       Demo Dry Run &
  Mock Listener       (Intake, Graph)       & Live Streaming      /memory View          Keyboard Nav          Screen Recording
```

1. **Phase 1 (Hours 0–3):**
   - Initialize `cli/package.json` with TypeScript, Ink, Commander.js, Vitest, and Zod.
   - Build base Ink `<Layout />` container (Header, Main Pane, Status Strip, Input Line) per `Frontend-Spec.md`.
   - Build mock SSE listener to test event rendering.
2. **Phase 2 (Hours 3–8):**
   - Implement **Intake View**, **Task Graph View** (`✓ ● ○ ✗`), and **Diff View**.
   - Build slash command router (`/plan`, `/diff`, `/trace`).
3. **Phase 3 (Hours 8–13):**
   - Connect Ink UI to FastAPI backend via `BackendApiClient.ts` and `SSEClient.ts`.
   - Implement **Trace View** (live test output) and **Reviewer Summary View**.
4. **Phase 4 (Hours 13–17):**
   - Build `<ApprovalPrompt />` UI dialog for out-of-scope execution requests (`[y/N]`).
   - Implement `<MemoryInspectView />` for `/memory` command and `/rollback` confirmation state.
5. **Phase 5 (Hours 17–21):**
   - Polish visual aesthetics (borders, colors, animation dots, status strip layout).
   - Add multi-task batch status view for benchmark evaluation.
6. **Phase 6 (Hours 21–24):**
   - Verify smooth terminal rendering without screen flicker or truncated lines.
   - Produce terminal recording/GIF assets for presentation.

---

## 5. Subsystem Dependencies & API Boundaries
- **CLI ↔ Backend REST API:** Calls `http://localhost:8000/api/v1/session`, `/plan`, `/run`, `/rollback`, `/memory`.
- **CLI ↔ Backend SSE Stream:** Listens to `http://localhost:8000/api/v1/events` for real-time state broadcasts.
- **Contract Guarantee:** All data received from backend is strictly validated at runtime using Zod schemas defined in `src/sse/sseTypes.ts`.

# Member 1 — Terminal CLI & Ink TUI (`@ae-01/cli`)

Terminal UI (TUI) frontend for the AE-01 Unified Agentic Coding Harness built with **Node.js**, **TypeScript**, **Ink** (React for Terminal), and **Commander.js**.

---

## 1. Quickstart & Usage

### Installation & Build
```bash
npm install
npm run build
```

### Running CLI REPL
```bash
# Start default interactive session
npm run dev

# Or run via compiled executable
node dist/index.js init --repo . --model claude-3-5-sonnet
```

### Running Tests
```bash
npm test
```

---

## 2. Interactive Slash Commands

| Slash Command | View State Triggered | Description |
|---|---|---|
| `/intake` | `IntakeView` | Shows repo scanning, AST symbol indexing, and git intake status. |
| `/plan` or `/graph` | `TaskGraphView` | Displays interactive task graph DAG with status indicators (`✓ ● ○ ✗`). |
| `/diff` or `/patch` | `DiffView` | Renders colorized unified git patch diff. |
| `/trace` or `/logs` | `TraceView` | Renders real-time test execution logs and verification runner. |
| `/summary` | `ReviewerSummaryView` | Renders patch proof, total cost, remaining uncertainty, and rollback path. |
| `/memory` | `MemoryInspectView` | Displays visual browser for 7 tiered memory tiers with provenance metadata. |
| `/rollback` | Action Trigger | Reverts target repo workspace to pre-run snapshot. |

---

## 3. Keyboard Navigation Shortcuts

- **`Tab`**: Cycle sequentially across the 6 active display views.
- **`Esc`**: Pause active run session.
- **`y` / `n`**: Respond to `<ApprovalPrompt />` safety confirmation popups.
- **`Enter`**: Submit task prompt or slash command.

---

## 4. Subsystem Integration Points

- **FastAPI REST Client:** `src/api/BackendApiClient.ts` -> targets `http://localhost:8000/api/v1`
- **SSE Stream Listener:** `src/sse/SSEClient.ts` -> targets `http://localhost:8000/api/v1/events`
- **Zod Runtime Event Validation:** `src/sse/sseTypes.ts`

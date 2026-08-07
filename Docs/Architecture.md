# AE-01 — Unified Agentic Coding Harness
### Architecture Document

---

## 1. Introduction and Scope

### Purpose
This document describes the architecture of the AE-01 Unified Agentic Coding Harness: a model-independent terminal coding agent that can understand, modify, test, debug, review, and maintain real repositories. It exists to prove that harness design — context construction, memory, orchestration, and verification — improves task performance under a fixed model and a fixed budget, independent of which underlying LLM is used.

### Intended audience
- **Developers and engineering teams** who will run the harness against their own repositories to complete bounded issues or features.
- **Evaluators / benchmark reviewers** who need to reproduce ablation results and inspect traces.
- **Contributors** extending the harness with new tools, memory backends, or model adapters.

### In scope
- A terminal CLI and Python backend that together onboard a repository, plan work, execute it in a sandbox, and verify it with real tests/builds/linters.
- A tiered memory system with provenance and invalidation.
- A model-independent adapter layer supporting multiple LLM providers.
- Benchmark tooling for Terminal-Bench, SWE-bench-style tasks, and organizer-provided hidden issues, including ablation runs.

### Out of scope
- Production deployment automation (the harness never receives deploy authority).
- Autonomous, unattended operation on repositories or credentials the user does not control.
- General-purpose browser automation or unrestricted host access.
- Long-term multi-project fleet management (the harness targets one repository/session at a time).

---

## 2. System Overview

### Big-picture diagram

```
                         ┌───────────────────────────┐
                         │        Developer           │
                         │   (terminal / keyboard)     │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌───────────────────────────┐
                         │      Terminal CLI (Ink)     │
                         │  session · rendering ·      │
                         │  approval prompts · views    │
                         └──────────────┬──────────────┘
                                        │ local HTTP + SSE
                                        ▼
                         ┌───────────────────────────┐
                         │     Python Backend (FastAPI)│
                         │  ───────────────────────── │
                         │  Model Adapter Layer         │
                         │  Repository Intelligence     │
                         │  Tiered Memory                │
                         │  Task Graph Orchestrator      │
                         │  Verification Pipeline        │
                         └───┬───────────┬───────────┬──┘
                             │           │           │
                 ┌───────────▼──┐  ┌─────▼─────┐ ┌───▼─────────────┐
                 │  LLM Providers │  │  Sandbox   │ │  Local Storage   │
                 │  (Anthropic,   │  │  (Docker)  │ │  (SQLite, files, │
                 │   OpenAI, etc.)│  │  git repo  │ │   traces, evidence)│
                 └────────────────┘  └────────────┘ └──────────────────┘
```

- The **developer** interacts only with the terminal CLI.
- The CLI never talks to models or the filesystem directly — every action is routed through the backend, which is the single source of truth for state.
- The backend calls out to **external LLM providers** over the network (only provider traffic leaves the machine) and to a **local Docker sandbox** that holds the actual working copy of the repository.
- All memory, traces, and evidence are persisted **locally** under the project workspace.

### External systems
- **LLM provider APIs** (Anthropic, OpenAI, or others) — swappable behind the model adapter.
- **Git remotes** — read for history/blame; pushes only happen if the user explicitly approves.
- **Package registries** (npm, PyPI, etc.) — reachable only from inside the sandbox, subject to network policy.

---

## 3. Component Architecture

### Component breakdown

```
┌─────────────────────────────────────────────────────────────────────┐
│ Terminal CLI (Node.js / TypeScript)                                   │
│  ├─ Session Manager        (session id, history, replay)              │
│  ├─ View Renderer (Ink)    (task graph, diff, trace, summary views)   │
│  ├─ Command Router         (slash-commands, approval prompts)         │
│  └─ SSE Client              (streams events from backend)              │
└───────────────────────────────┬─────────────────────────────────────┘
                                 │ HTTP / SSE
┌───────────────────────────────▼─────────────────────────────────────┐
│ Backend API Layer (FastAPI)                                           │
│  ├─ /session   /plan   /run   /memory   /trace   /rollback endpoints  │
└───────┬─────────────┬─────────────┬─────────────┬────────────────────┘
        │             │             │             │
┌───────▼──────┐ ┌────▼────────┐ ┌──▼──────────┐ ┌▼─────────────────┐
│ Model Adapter │ │ Repository   │ │ Task Graph  │ │ Verification      │
│ Layer          │ │ Intelligence │ │ Orchestrator│ │ Pipeline           │
│ ────────────── │ │ ──────────── │ │ ─────────── │ │ ────────────────── │
│ provider clients│ │ file map     │ │ plan/replan │ │ build/test/lint    │
│ prompt assembly │ │ AST/symbol   │ │ specialist  │ │ static analysis    │
│ streaming        │ │ index        │ │ sub-agents  │ │ regression tests   │
│ cost/token track │ │ call graphs  │ │ checkpoints │ │ hidden eval tasks  │
└────────┬────────┘ │ git history  │ │ early term. │ └─────────┬─────────┘
         │           └──────┬───────┘ └──────┬──────┘            │
         │                  │                │                   │
┌────────▼──────────────────▼────────────────▼───────────────────▼────┐
│ Tiered Memory + Context Manager                                       │
│  working · task · project · episodic · procedural · preference ·      │
│  evidence — each item carries provenance and an invalidation rule      │
└────────────────────────────────┬──────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼─────────────────────────────────────┐
│ Sandboxed Execution Service (Docker)                                    │
│  scoped filesystem · network policy · resource limits · secret          │
│  isolation · snapshots · approval gates · emergency termination          │
└──────────────────────────────────────────────────────────────────────┘
```

### How components talk to each other
- **CLI → Backend**: REST calls for commands (`/run`, `/rollback`) and a persistent SSE stream for live updates (plan steps, tool calls, test results).
- **Model Adapter Layer**: the *only* component that talks to LLM providers. Every other component requests a "completion" through this layer, so swapping models requires no other code changes.
- **Task Graph Orchestrator**: drives the run — it asks the Model Adapter for plans/patches, asks Repository Intelligence for context, asks the Context Manager for a token-budgeted prompt, and dispatches shell/tool calls to the Sandbox.
- **Verification Pipeline**: invoked by the Orchestrator after each coding step; results (pass/fail, evidence) are written back into Tiered Memory and drive replanning or completion.
- **Sandbox**: the only component with filesystem/network access to the actual repository; everything else operates on indexes, summaries, or evidence records, not raw uncontrolled access.

---

## 4. Data Design

### Storage overview
| Store | Technology | Purpose |
|---|---|---|
| Memory store | SQLite (via SQLAlchemy) | Tiered memory items with provenance/invalidation |
| Repository index | SQLite + on-disk cache | File map, symbol index, call graph, test-to-source map |
| Trace/evidence log | Append-only JSONL files | Plan revisions, tool calls, test results, cost/token usage |
| Session state | SQLite | Active session, task graph state, checkpoints |
| Sandbox workspace | Docker volume / bind mount | Live working copy of the repository under edit |

### Entity-relationship diagram (memory & session domain)

```
┌────────────────┐        ┌────────────────────┐        ┌───────────────────┐
│   Session        │ 1    * │   TaskGraphNode      │ 1    * │   ToolCall           │
│ ───────────────── │───────▶│ ───────────────────── │───────▶│ ───────────────────── │
│ id (PK)           │        │ id (PK)                │        │ id (PK)                │
│ repo_path          │        │ session_id (FK)        │        │ node_id (FK)           │
│ model_provider      │        │ parent_id (FK, nullable)│        │ command                │
│ started_at          │        │ status                  │        │ exit_code              │
│ ended_at            │        │ type                    │        │ stdout_ref             │
└─────────┬──────────┘        │ created_at              │        │ started_at              │
          │ 1                 └───────────┬─────────────┘        └───────────────────────┘
          │                               │ 1
          │ *                             │ *
┌─────────▼──────────┐        ┌───────────▼─────────────┐        ┌───────────────────────┐
│   MemoryItem          │        │   EvidenceRecord           │        │   VerificationRun        │
│ ───────────────────── │        │ ─────────────────────────── │        │ ───────────────────────── │
│ id (PK)                │        │ id (PK)                      │        │ id (PK)                    │
│ session_id (FK)        │        │ node_id (FK)                 │        │ node_id (FK)               │
│ tier (enum)             │        │ kind (repro/test/patch/...)  │        │ suite (build/lint/test/...) │
│ content                 │        │ content_ref                  │        │ result (pass/fail)          │
│ provenance              │        │ created_at                    │        │ log_ref                    │
│ invalidation_rule       │        └───────────────────────────────┘        └───────────────────────────┘
│ created_at              │
└─────────────────────────┘
```

- `Session` is the root entity for one CLI run against one repository.
- `TaskGraphNode` forms a self-referencing tree/DAG (`parent_id`) representing sequential and parallel branches.
- `MemoryItem` is tagged by tier (working, task, project, episodic, procedural, preference, evidence) and always carries `provenance` (where the fact came from) and an `invalidation_rule` (when it stops being trusted).
- `EvidenceRecord` and `VerificationRun` are what the Reviewer Summary view and the final report are built from — never raw model output.

---

## 5. Non-Functional Requirements

### Security
- The sandbox runs with a **scoped filesystem** (only the target repository workspace) and a **default-deny network policy**, with explicit allowlists per task.
- The harness **never receives** unrestricted host credentials, SSH keys, browser sessions, or production deploy authority (hard safety boundary, not configurable).
- Secrets discovered in the repository or environment are isolated from the model context and redacted in traces.
- Every filesystem-mutating or network-reaching command outside the pre-approved scope triggers an **approval gate** before execution.
- An **emergency termination** path exists at all times, killing the sandbox and halting the run.

### Performance
- Context assembly targets a bounded token budget per turn, with relevance scoring and hierarchical summarization to avoid re-sending full files.
- Repository indexing (file map, AST/symbol index, call graph) is incremental — only files changed since the last snapshot are re-indexed.
- SSE streaming keeps CLI-perceived latency low; the user sees plan/tool-call progress as it happens rather than waiting for the full run.

### Scalability
- The Task Graph Orchestrator supports **bounded parallel branches** with independent specialist sub-agents, so independent sub-tasks (e.g., patch + test update) can run concurrently within a resource cap.
- The backend is stateless aside from its local stores, so multiple backend instances could in principle serve multiple concurrent sessions on a shared machine, each with its own sandbox and workspace.

### Reliability & recoverability
- Checkpoints are written at each task-graph node boundary, enabling resume-after-failure and reproducible ablation runs (cold/warm memory).
- The Verification Pipeline is the sole arbiter of "done" — a run is never marked complete on model confidence alone.
- Every completed run produces a **rollback-ready patch**, so any change can be reverted without manual archaeology.

### Observability
- Traces expose plan revisions, retrieved context, tool calls, files touched, tests run, failures, recovery actions, and token/cost usage.
- Hidden chain-of-thought is never surfaced — only actions and their results are logged, keeping the trace both useful and safe to share.

---

## 6. Decisions and Trade-offs (ADRs)

### ADR-001: Split CLI and backend into separate processes
- **Decision**: The terminal CLI (Node/TypeScript) and the orchestration engine (Python) run as separate processes communicating over local HTTP/SSE, rather than a single monolithic CLI.
- **Reasoning**: Python has the strongest ecosystem for ML/orchestration tooling (LangGraph-style graphs, embeddings, static analysis bindings), while Node/Ink is the best fit for a responsive terminal UI. Separating them also lets either side be swapped or scaled independently.
- **Trade-off**: Adds an IPC boundary and serialization overhead versus an in-process design; mitigated by keeping the protocol thin (SSE + simple REST).

### ADR-002: Verification-first completion, not model confidence
- **Decision**: A task is only marked complete when builds, tests, linters, and static analysis pass — never based on the model asserting it's done.
- **Reasoning**: This is the harness's core differentiator and directly supports the benchmark goal of separating model capability from harness-driven verification gains.
- **Trade-off**: Slower iteration on tasks with weak or missing test coverage; the harness must fall back to static analysis and reproduction evidence in those cases.

### ADR-003: Sandboxed execution via Docker rather than direct host execution
- **Decision**: All commands run inside a Docker sandbox with scoped filesystem, network policy, and resource limits.
- **Reasoning**: Required by the stated safety boundary — the harness must never hold unrestricted host credentials or touch files outside the target repository.
- **Trade-off**: Adds container startup latency and requires Docker as a dependency; accepted because safety isolation is non-negotiable.

### ADR-004: Model-independent adapter layer as a hard architectural boundary
- **Decision**: All LLM calls are routed through a single adapter interface; no other component is allowed to call a provider SDK directly.
- **Reasoning**: Enables the required "same model, baseline vs. submitted harness" comparison and "model replacement without harness changes" hard-mode extension.
- **Trade-off**: Slightly more indirection for simple completions; accepted since it's central to the project's proof-of-quality requirement.

### ADR-005: SQLite for memory and indexing rather than a hosted database
- **Decision**: Use SQLite (via SQLAlchemy) for tiered memory, session state, and repository indexes.
- **Reasoning**: Keeps the harness fully local and dependency-light for a single-repository, single-developer session; matches the "no data leaves the machine" requirement.
- **Trade-off**: Not designed for concurrent multi-user access; acceptable since each session owns its own workspace and store.

### ADR-006: Provenance and invalidation rules required on every memory item
- **Decision**: Every `MemoryItem` must record where it came from and when it should stop being trusted, enforced at the schema level (Pydantic).
- **Reasoning**: Directly required by the problem statement and necessary to detect and handle deliberately stale project memory (a named hard-mode extension).
- **Trade-off**: Slightly more write overhead per memory item; considered essential rather than optional.

---

*This document should be read alongside the Tech Stack Overview and the Frontend Spec; together they describe what the harness is built from, how it is structured, and what the user sees.*

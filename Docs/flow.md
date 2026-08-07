# AE-01 — Unified Agentic Coding Harness
## 24-Hour Hackathon Execution Flow & 5-Member Work Allocation

---

## 1. Overview & Objectives

This document defines the 24-hour execution roadmap and work division for a **5-member engineering team** building the **AE-01 Unified Agentic Coding Harness**. 

The goal of the 24-hour sprint is to construct a fully functional, model-independent, terminal-based coding harness that autonomously navigates repository understanding, planning, sandboxed execution, and verification-first completion while producing benchmark-credible ablation evidence.

### Primary References in `@Docs`
- [PRD.md](file:///c:/Users/HP/Hackathon/Billu-Gang/Docs/PRD.md) — Product Requirements, Success Metrics, Functional & Non-Functional Requirements.
- [Architecture.md](file:///c:/Users/HP/Hackathon/Billu-Gang/Docs/Architecture.md) — System Architecture, Component Interfaces, Data Schema, ADRs.
- [Tech-Stack.md](file:///c:/Users/HP/Hackathon/Billu-Gang/Docs/Tech-Stack.md) — Language breakdown, Frameworks, Libraries, Transport mechanisms.
- [Frontend-Spec.md](file:///c:/Users/HP/Hackathon/Billu-Gang/Docs/Frontend-Spec.md) — Ink TUI Layout, Region Breakdown, View States, Interaction Model.

---

## 2. Team Roles & Component Ownership

The codebase is partitioned into 5 independent, well-bounded ownership domains corresponding to the 8 core engineering surfaces outlined in [PRD.md](file:///c:/Users/HP/Hackathon/Billu-Gang/Docs/PRD.md).

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MEMBER 1: TERMINAL CLI                                  │
│             (Node.js / TypeScript / Ink / Commander.js / SSE Streaming Client)            │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │ Local REST + SSE
┌───────────────────────────────────────────▼─────────────────────────────────────────────┐
│                                MEMBER 2: BACKEND CORE                                   │
│            (FastAPI Server / Model Adapter Layer / Token & Cost Tracking)               │
└───────────┬───────────────────────────────┬───────────────────────────────┬─────────────┘
            │                               │                               │
┌───────────▼─────────────┐     ┌───────────▼─────────────┐     ┌───────────▼─────────────┐
│    MEMBER 3: REPO &     │     │     MEMBER 4: TASK      │     │  MEMBER 5: VERIFY &     │
│       MEMORY LEAD       │     │     ORCHESTRATOR        │     │     BENCHMARK LEAD      │
│ (Tree-sitter / SQLite   │     │ (LangGraph / Docker     │     │ (Pytest / Trace /       │
│  Tiered Memory / RAG)   │     │  Sandbox / Approval)    │     │  Ablations / Reviewer)  │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

### Detailed Ownership Matrix

| Member | Primary Role | Core Engineering Surfaces Owned | Tech Stack & Tools | Key Deliverables |
|---|---|---|---|---|
| **Member 1** | **Terminal CLI & TUI Lead** | User Interface, Interactive REPL, Approval Prompts, Live Event Rendering | TypeScript, Ink, Commander.js, Vitest, Zod | Ink layout (Header, Main Pane, Status Strip, Command Line), 5 Main Pane Views, Slash-command router, SSE client. |
| **Member 2** | **Backend Core & Model Adapter Lead** | Model Adapter Layer, FastAPI Server Infrastructure, Token & Cost Attribution | Python 3.11, FastAPI, Pydantic, Anthropic SDK, OpenAI SDK, `httpx`, `sse-starlette` | FastAPI app, pluggable model adapters (Anthropic/OpenAI), SSE streaming endpoint, cost & token tracker API. |
| **Member 3** | **Repo Intelligence & Tiered Memory Lead** | Repository Intelligence, Tiered Memory Engine, Context Manager | Tree-sitter, GitPython, ripgrep, SQLite (SQLAlchemy), sentence-transformers, tiktoken | AST symbol indexer, git blame parser, SQLite memory store with provenance & invalidation, token budget context ranker. |
| **Member 4** | **Task Orchestrator & Sandbox Security Lead** | Task Graph Orchestrator, Sandboxed Execution Service, Safety Boundaries | LangGraph / Async State Graph, Docker SDK (`docker-py`), Asyncio, Git snapshotting | DAG task planner with sub-agents, Docker container manager, filesystem/network approval gates, emergency stop, rollback. |
| **Member 5** | **Verification, Benchmarking & Evaluation Lead** | Verification Pipeline, Benchmark Runner, Trace & Reviewer View Backend | Pytest, OpenTelemetry, Terminal-Bench, SWE-bench scripts, ESLint, Mypy, Ruff | Automated verification test runner, trace recorder, reviewer summary generator, ablation runner (memory on/off, baseline vs. submitted). |

---

## 3. 24-Hour Phase Breakdown

The 24-hour hackathon is structured into **6 distinct phases** of 3 to 5 hours each, punctuated by mandatory integration sync checkpoints.

```
Hour 0     3          8               13              17              21           24
  │ Phase 1 │  Phase 2 │    Phase 3    │    Phase 4    │    Phase 5    │  Phase 6   │
  ├─────────┼──────────┼───────────────┼───────────────┼───────────────┼────────────┤
  │ Setup & │ Subsystem│ E2E System    │ Advanced      │ Benchmarks &  │ Demo Dry   │
  │ Contract│ Core Dev │ Integration   │ Verification  │ Ablations     │ Run & Freeze
  SYNC 1   SYNC 2     SYNC 3          SYNC 4          SYNC 5          SYNC 6
```

---

### Phase 1: Environment Setup, Architecture & Contract Freeze (Hours 0 – 3)
**Goal:** Establish repository workspace structure, freeze API/SSE schemas, and deliver mockable subsystem interfaces.

- **Sync Checkpoint 1 (Hour 3.0):** API Contract Freeze. All Pydantic data schemas, REST routes, and SSE event payloads locked.

#### Individual Member Tasks
* **Member 1 (CLI):** 
  * Initialize Node.js/TypeScript project with Ink and Commander.js.
  * Implement base layout container (Header Bar, Main Pane, Status Strip, Input Line) as specified in [Frontend-Spec.md](file:///c:/Users/HP/Hackathon/Billu-Gang/Docs/Frontend-Spec.md).
  * Build mock SSE listener to render incoming stream events.
* **Member 2 (Backend Core):** 
  * Initialize FastAPI application skeleton and directory structure.
  * Define core Pydantic models for `Session`, `TaskGraphNode`, `ToolCall`, `MemoryItem`, `EvidenceRecord`, and `VerificationRun` matching Section 4 of [Architecture.md](file:///c:/Users/HP/Hackathon/Billu-Gang/Docs/Architecture.md).
  * Build SSE event broadcaster (`sse-starlette`) and endpoint stubs (`/session`, `/plan`, `/run`).
* **Member 3 (Repo & Memory):**
  * Set up SQLite database schema via SQLAlchemy for Tiered Memory and Repository Indexes.
  * Create base AST parser structure using `tree-sitter` for Python/TypeScript symbol extraction.
  * Implement basic file scanner and ignore parser (`.gitignore`).
* **Member 4 (Orchestration & Sandbox):**
  * Build Docker base image for sandboxed execution environment (Python + Node + Git + basic CLI tools).
  * Implement Python `DockerSandbox` class with scoped workspace volume mount and resource limits (CPU/Memory caps).
  * Stub out emergency kill mechanism and approval gate callback interface.
* **Member 5 (Verification & Benchmark):**
  * Set up test suite for the harness project (`pytest`).
  * Design standard JSONL trace schema (`trace.jsonl`) for event logging (plan changes, tool invocations, test outputs).
  * Prepare test target repositories (1 sample bug repo + 1 benchmark test issue).

---

### Phase 2: Core Subsystem Implementation (Hours 3 – 8)
**Goal:** Build functional domain logic within each isolated module before wiring up end-to-end communication.

- **Sync Checkpoint 2 (Hour 8.0):** Subsystem Integration Readiness. Each module passes isolated unit tests.

#### Individual Member Tasks
* **Member 1 (CLI):**
  * Implement **Repository Intake View** (scanning progress, checkmarks, spinners).
  * Implement **Task Graph View** (tree rendering, status icons `✓ ● ○ ✗`).
  * Implement **Diff View** (syntax-highlighted unified diff with `+` green and `-` red).
  * Implement basic command input router for slash commands (`/plan`, `/diff`, `/trace`).
* **Member 2 (Backend Core):**
  * Implement `ModelAdapter` base interface and concrete adapters (`AnthropicAdapter`, `OpenAIAdapter`).
  * Integrate prompt formatting and tool-calling schema translation.
  * Implement token usage counting (`tiktoken`) and real-time cost calculation ($/1k tokens) appended to each completion trace.
* **Member 3 (Repo & Memory):**
  * Build full symbol graph and import/call graph using `tree-sitter` and `networkx`.
  * Build test-to-source file mapping logic (associating `test_paginator.py` with `paginator.py`).
  * Implement `TieredMemoryStore` CRUD methods supporting memory tiers (working, task, project, episodic, procedural, preference, evidence).
* **Member 4 (Orchestration & Sandbox):**
  * Implement `TaskGraphOrchestrator` using state graph logic (planning node → execution node → verification node).
  * Implement sandboxed command execution service (`sandbox.exec_command("pytest")`).
  * Build filesystem snapshotting (`git commit` / patch checkpoints inside sandbox) for rollback support.
* **Member 5 (Verification & Benchmark):**
  * Build `VerificationPipeline` service to trigger build, lint (Ruff/ESLint), type check (Mypy), and test runner inside sandbox.
  * Implement parser for standard test outputs (pytest XML/JSON format, npm test output).
  * Build `TraceLogger` to capture all system events asynchronously.

---

### Phase 3: End-to-End System Integration & First Autonomous Patch (Hours 8 – 13)
**Goal:** Connect CLI to FastAPI backend and run the first complete loop: User Input → Plan Generation → Tool Execution in Docker → Code Edit → Verification Run → TUI Output.

- **Sync Checkpoint 3 (Hour 13.0):** First E2E Patch Run. Harness successfully ingests issue, edits target repo in Docker, passes test, and surfaces summary in CLI.

#### Individual Member Tasks
* **Member 1 (CLI):**
  * Connect Ink UI to backend REST endpoints and live SSE stream.
  * Implement **Verification / Trace View** with live streaming test updates and timing.
  * Implement **Reviewer Summary View** displaying completed patch details, token costs, and rollback commands.
* **Member 2 (Backend Core):**
  * Wire Model Adapter output directly into Orchestrator tool call dispatch loop.
  * Ensure stream handler emits real-time events (`plan_updated`, `tool_started`, `tool_finished`, `verification_started`, `verification_finished`).
  * Expose `/rollback` endpoint to trigger sandbox workspace reset.
* **Member 3 (Repo & Memory):**
  * Integrate Context Manager into Model Adapter call chain: dynamically budget context window and rank symbols by relevance.
  * Implement automatic memory invalidation when target files are updated (FR11).
  * Add prompt-injection sanitization for external files and issue descriptions (FR17).
* **Member 4 (Orchestration & Sandbox):**
  * Connect Orchestrator to Sandbox: execute model tool calls (file edit, shell execution) inside container.
  * Implement approval gate handler: pause execution and await CLI approval when command exceeds safe scope.
  * Validate sandboxed execution isolation (verify host network/filesystem cannot be touched).
* **Member 5 (Verification & Benchmark):**
  * Integrate Verification Pipeline into Orchestrator: automatically run verification suite after code modifications.
  * Build basic SWE-bench / Terminal-Bench problem loader to feed sample issue into harness.
  * Create Reviewer Summary backend engine aggregating completeness proof, uncertainties, and rollback path.

---

### Phase 4: Advanced Features, Recovery Loops & Hardening (Hours 13 – 17)
**Goal:** Implement error recovery, failure self-healing (MVD requirement), tiered memory provenance controls, and safety enforcement.

- **Sync Checkpoint 4 (Hour 17.0):** Failure Recovery Pass. Harness detects an injected failing test, replans, applies fix, and re-verifies successfully.

#### Individual Member Tasks
* **Member 1 (CLI):**
  * Implement interactive approval prompt UI for out-of-scope commands (`[y/N]` prompt in command line).
  * Add `/memory` command view allowing user to inspect, edit, export, and delete items across tiers (FR12).
  * Add `/rollback` confirmation and execution feedback state.
* **Member 2 (Backend Core):**
  * Add fallback model adapter switching (e.g. automatic fallback to secondary model on rate limit or context failure).
  * Implement session serialization and resume mechanism.
  * Refine API error handling to prevent backend crashes on malformed LLM responses.
* **Member 3 (Repo & Memory):**
  * Add metadata provenance tracking (source file, timestamp, model ID, confidence score) to all `MemoryItem` records (FR10).
  * Build incremental repo index refresher triggered after every sandbox code edit (FR8).
  * Implement hierarchical file summarization for files exceeding token context budget (FR15).
* **Member 4 (Orchestration & Sandbox):**
  * Implement dynamic replanning loop: when verification fails, feed error back into Task Graph to generate patch revision (FR22).
  * Implement emergency stop route (`/pause` / `Ctrl+C` interrupt) that immediately SIGKILLs running sandbox commands (FR28).
  * Enforce default-deny network policy inside container (NFR7, NFR8).
* **Member 5 (Verification & Benchmark):**
  * Implement injected failure recovery test case for live demo (FR40).
  * Build regression test runner comparing current repo state against initial git snapshot (FR30).
  * Build evaluator grader for hidden test injection (FR31).

---

### Phase 5: Benchmark Execution, Ablations & Report Generation (Hours 17 – 21)
**Goal:** Execute benchmark runs (Terminal-Bench / SWE-bench), run controlled ablation studies, and verify all success metrics.

- **Sync Checkpoint 5 (Hour 21.0):** Benchmark Data Lock. Ablation metrics, cost numbers, and pass rates finalized and logged.

#### Individual Member Tasks
* **Member 1 (CLI):**
  * Polish TUI visual aesthetics (color coding, borders, animation dots, status strip layout).
  * Add benchmark evaluation progress view showing multi-task batch status.
  * Verify keyboard navigation smoothness across all 5 views.
* **Member 2 (Backend Core):**
  * Run model independence verification: run test suite switching between Anthropic and OpenAI adapters with zero code changes (NFR10).
  * Collect overall token usage, wall-clock latency, and total API cost statistics for the benchmark report.
* **Member 3 (Repo & Memory):**
  * Verify memory ablation flags: memory ON vs. memory OFF (cold vs. warm memory retrieval).
  * Benchmark index retrieval latency ensuring context assembly stays under 20% total wall-clock time (NFR2).
* **Member 4 (Orchestration & Sandbox):**
  * Perform load testing on Docker sandbox lifecycle: verify container cleanup and disk isolation.
  * Test multi-branch execution with parallel sub-agents (FR19).
* **Member 5 (Verification & Benchmark):**
  * Execute Terminal-Bench and SWE-bench test sets.
  * Run controlled **ablation protocol** (FR47):
    1. Baseline Harness vs. Submitted Harness (same model & budget).
    2. Tiered Memory ON vs. Tiered Memory OFF.
    3. Single Agent vs. Multi-Agent Task Graph.
  * Generate standardized **Ablation & Performance Report** artifact.

---

### Phase 6: Demonstration Dry Run, Documentation & Code Freeze (Hours 21 – 24)
**Goal:** Conduct complete dry runs of the Minimum Viable Demonstration (MVD FR37–FR42), finalize docs, and freeze repository.

- **Sync Checkpoint 6 (Hour 23.0):** Code Freeze. Zero new features; only critical bug fixes allowed.

#### Individual Member Tasks
* **Member 1 (CLI):**
  * Ensure full demo flow renders flawlessly without screen flicker or truncated lines.
  * Create terminal demo recording / GIF assets for presentation.
* **Member 2 (Backend Core):**
  * Perform security audit: ensure no API keys or local host credentials leak into traces or memory DBs.
  * Finalize FastAPI OpenAPI documentation (`/docs`).
* **Member 3 (Repo & Memory):**
  * Verify clean database initialization script for fresh user onboarding (`harness init`).
* **Member 4 (Orchestration & Sandbox):**
  * Validate quick-start setup scripts (`docker build`, python environment setup).
* **Member 5 (Verification & Benchmark):**
  * Finalize final demonstration script and pitch evidence output.
  * Populate `walkthrough.md` with benchmark proof, screenshots, and ablation data.

---

## 4. Phase vs. Member Responsibility Matrix

| Phase / Hours | Member 1 (CLI) | Member 2 (Backend Core) | Member 3 (Repo & Memory) | Member 4 (Orchestration) | Member 5 (Verification & Bench) |
|---|---|---|---|---|---|
| **Phase 1**<br>*(H0 – H3)* | Ink Layout Boilerplate & Mock SSE Listener | FastAPI Skeleton, Pydantic Schemas, SSE Broadcaster | SQLite DB Setup, Tree-sitter Parser Setup | Base Docker Image, Container Manager | Pytest Infrastructure, JSONL Trace Schema |
| **Phase 2**<br>*(H3 – H8)* | Intake, Task Graph, and Diff Views in Ink | Anthropic/OpenAI Adapters, Cost/Token Tracker | AST Symbol Indexer, Tiered Memory CRUD | Task Graph DAG, Sandboxed Exec Shell | Verification Pipeline (build/lint/test) |
| **Phase 3**<br>*(H8 – H13)* | Trace & Reviewer Views, Backend SSE Link | REST API & Tool Dispatch Loop, Rollback Endpoint | Context Manager Ranking, Memory Auto-Invalidation | Tool Call Execution in Docker, Approval Gates | E2E Integration Test, Reviewer Summary Builder |
| **Phase 4**<br>*(H13 – H17)* | Approval UI Prompt, `/memory` Inspect View | Adapter Fallback System, Session Persistence | Memory Provenance Metadata, Repo Re-Indexer | Replanning Engine, Emergency Stop (SIGKILL) | Injected Failure Self-Healing Demo Test |
| **Phase 5**<br>*(H17 – H21)* | TUI Aesthetic Polish, Multi-Task View | Model Independence Test, Total Cost Report | Memory Ablation Config, Retrieval Profiling | Parallel Sub-Agent Test, Container Cleanup | Run Terminal-Bench & SWE-bench Ablations |
| **Phase 6**<br>*(H21 – H24)* | TUI Demo Scripting & Visual Recording | Security Audit & Final OpenAPI Spec | Clean Setup Script (`harness init`) | Quick-Start Setup Validation | Final Walkthrough & Pitch Artifacts |

---

## 5. Integration Sync Checkpoints & Protocols

To avoid integration debt during a 24-hour sprint, all 5 members must join a **10-minute standup** at each sync checkpoint.

```
       ┌─────────────────────────────────────────────────────────┐
       │               MANDATORY SYNC CHECKPOINTS                │
       ├─────────────────────────────────────────────────────────┤
       │ SYNC 1 (H03.00) : API Schemas & Data Contracts Locked    │
       │ SYNC 2 (H08.00) : Individual Subsystem Unit Tests Pass │
       │ SYNC 3 (H13.00) : First E2E Autonomous Patch Complete    │
       │ SYNC 4 (H17.00) : Self-Healing Failure Loop Verified   │
       │ SYNC 5 (H21.00) : Ablation Results & Benchmark Finalized│
       │ SYNC 6 (H23.00) : Code Freeze & Final Demo Dry Run     │
       └─────────────────────────────────────────────────────────┘
```

### Protocol for Inter-Subsystem Dependencies
1. **CLI ↔ Backend:** All communication MUST strictly use the JSON REST endpoints and SSE payload schemas defined in Phase 1. No direct subprocess calls from Node.js to Python.
2. **Orchestrator ↔ Model Adapter:** Orchestrator requests completions ONLY via the `ModelAdapter` interface. Raw SDK calls outside the adapter are blocked in code review.
3. **Orchestrator ↔ Sandbox:** No host command execution. All file edits and bash scripts MUST execute through `DockerSandbox.exec_command()`.

---

## 6. Risk Management & Emergency Protocols

| Risk Scenario | Impact | Primary Owner | Mitigation & Contingency Strategy |
|---|---|---|---|
| **Docker execution slow or permissions fail on host** | High | Member 4 | Fallback to isolated local virtual environment sandbox (`venv` + directory isolation) with explicit warning. |
| **LLM Provider Rate Limits / API Outages** | High | Member 2 | Adapter instantly switches to backup provider (e.g. Anthropic → OpenAI) or local vLLM mock server. |
| **Ink TUI screen flickering or terminal rendering bugs** | Medium | Member 1 | Fallback to simplified single-pane line-by-line streaming terminal mode (`Commander.js` basic output). |
| **Tree-sitter fails on complex polyglot repo files** | Medium | Member 3 | Fallback to regex symbol search + `ripgrep` for structural indexing. |
| **Benchmark run times out in 24h window** | High | Member 5 | Pre-select a subset of 5 representative SWE-bench / Terminal-Bench tasks for ablation validation. |

---

## 7. Minimum Viable Demonstration (MVD) Checklist

By Hour 23, the team must successfully demonstrate the following workflow (per FR37–FR42 in [PRD.md](file:///c:/Users/HP/Hackathon/Billu-Gang/Docs/PRD.md)):

- [ ] **Repository Onboarding:** Run `harness init` on an unseen repo; CLI displays file indexing, AST symbol graph generation, and git history intake.
- [ ] **Issue Intake & Plan Display:** Submit a bug report; TUI renders an interactive, multi-node task graph.
- [ ] **Issue Reproduction:** Harness runs verification test inside Docker sandbox, reproduces failure, and records evidence *before* writing code edits.
- [ ] **Autonomous Patch & Self-Healing:** Harness applies patch; an intentional test failure is encountered; harness self-diagnoses, replans, patches, and re-tests until green.
- [ ] **Verification-First Done:** All build, lint, type-check, and unit test suites pass; task marked complete strictly on test proof.
- [ ] **Ablation Comparison:** Surface evidence report showing Δ pass rate and cost savings of submitted harness vs. baseline harness under identical LLM model and budget constraints.
- [ ] **Reviewer View & Rollback:** TUI displays summary (Why Complete, Remaining Uncertainty, Rollback Command); issue `/rollback` to demonstrate instant clean workspace restoration.

---

*This document serves as the operational guide for the 24-hour hackathon. Any changes to subsystem interfaces must be agreed upon by all affected owners during a sync checkpoint.*

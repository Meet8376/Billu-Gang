# AE-01 — Unified Agentic Coding Harness
### Technology Stack Overview

---

## System Overview

The harness is a model-independent coding agent split into two cooperating processes: a lightweight terminal CLI that owns the user-facing session, rendering, and command loop, and a Python backend service that owns repository intelligence, memory, orchestration, sandboxed execution, and verification. The CLI and backend communicate over a local IPC/HTTP boundary so either side can be swapped, versioned, or scaled independently.

- **Terminal CLI (Node.js/TypeScript):** interactive REPL, streaming output, approval prompts, trace viewer, and plan/diff rendering.
- **Python backend:** model adapter layer, repository indexing, tiered memory, task graph orchestration, sandboxed command execution, and verification pipeline.
- **Transport:** local HTTP + Server-Sent Events (SSE) for streaming plans, tool calls, and test output back to the CLI.
- **Storage:** on-disk project workspace for memory, traces, and evidence artifacts; no data leaves the machine unless the user configures a remote model provider.

---

## Requirements

### Functional requirements
- Onboard an arbitrary repository and build a file map, symbol index, and test-to-source mapping.
- Accept a bounded issue or feature request and produce an explicit, inspectable task graph.
- Execute coding steps inside a sandboxed shell with scoped filesystem and network access.
- Run builds, tests, linters, type checks, and static analysis as the source of truth for completion, not model confidence.
- Persist tiered memory (working, task, project, episodic, procedural, preference, evidence) with provenance and invalidation.
- Support model swap-in/swap-out without changes to harness logic (model-independent adapter).
- Produce a rollback-ready patch plus a cost/latency/evidence report for every run.

### Non-functional requirements
- Cross-platform terminal support (macOS, Linux, WSL) with a responsive, low-latency streaming UI.
- Deterministic, reproducible benchmark runs for ablations (memory on/off, single/multi-agent, cold/warm memory).
- Strict sandbox isolation: no unrestricted host credentials, SSH keys, browser sessions, or deploy authority.
- Observability without leaking hidden chain-of-thought: plan revisions, tool calls, files touched, and evidence only.
- Graceful recovery from at least one injected failure per run, with emergency termination available at any time.

---

## Languages

| Component | Language |
|---|---|
| Terminal CLI | TypeScript (compiled to Node.js/JavaScript) |
| Backend service | Python 3.11+ |
| Sandboxed task scripts | Shell / Bash, with Python and Node runtimes available inside the sandbox |
| Config & schemas | YAML / JSON, JSON Schema for validation |

---

## Frameworks

### CLI (Node.js / TypeScript)
- **Ink** — React-based framework for building the interactive terminal UI (streaming panes, diff views, approval prompts).
- **Commander.js** — command parsing and subcommand structure (init, run, review, replay).
- **Vitest** — unit and integration testing for the CLI package.

### Backend (Python)
- **FastAPI** — local HTTP + SSE service exposing session, planning, memory, and execution endpoints to the CLI.
- **Pydantic** — typed schemas for task graphs, memory items, tool calls, and evidence records.
- **LangGraph** (or a hand-rolled equivalent) — task graph execution with sequential/parallel branches, checkpoints, and replanning.
- **Celery / asyncio task queues** — bounded specialist agent scheduling and parallel branch execution.
- **pytest** — backend unit, integration, and ablation test suites.

---

## Libraries

### Repository intelligence
- **tree-sitter** (Python bindings) — polyglot AST parsing and symbol indexing.
- **GitPython** — git history, blame, and diff inspection.
- **ripgrep** (invoked via subprocess) — fast repository-wide search.
- **networkx** — import/call graph construction and traversal.

### Memory & context
- **SQLite** (via SQLAlchemy) — tiered memory store with provenance metadata.
- **sentence-transformers** / a local embedding model — relevance scoring and semantic retrieval over memory and code.
- **tiktoken** — token counting for dynamic context budgeting.

### Model adapter layer
- **Anthropic Python SDK, OpenAI Python SDK** — pluggable model backends behind a common adapter interface.
- **httpx** — async HTTP client used inside the adapter layer for provider calls.

### Sandboxed execution & verification
- **Docker SDK for Python** (docker-py) — scoped filesystem/network sandboxes, snapshots, and resource limits.
- **subprocess / asyncio.subprocess** — running builds, tests, linters, and type checkers inside the sandbox.
- **coverage.py, ESLint, mypy, ruff** — language-specific lint/type-check tooling invoked during verification.

### Observability & CLI-backend bridge
- **OpenTelemetry** (Python SDK) — structured tracing of plan revisions, tool calls, and recovery actions.
- **sse-starlette** — server-sent event streaming from FastAPI to the terminal CLI.
- **Zod** — runtime validation of streamed payloads on the CLI/TypeScript side.

---

*This stack keeps the CLI thin and portable while concentrating repository intelligence, memory, orchestration, and verification — the harness's core contribution — in a testable, swappable Python backend.*

# AE-01 — Unified Agentic Coding Harness
## Master Directory Structure & Team Work Breakdown Index

---

## 1. Executive Summary & Team Domain Map

The **AE-01 Unified Agentic Coding Harness** is partitioned into 5 well-bounded engineering domains corresponding to the 5 team members. Each team member has a dedicated, non-overlapping ownership directory within the project repository.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MEMBER 1: TERMINAL CLI                                  │
│                             (cli/ package in TypeScript/Ink)                            │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │ Local HTTP REST + SSE Stream
┌───────────────────────────────────────────▼─────────────────────────────────────────────┐
│                                MEMBER 2: BACKEND CORE                                   │
│                     (backend/core/ package in FastAPI / Pydantic)                         │
└───────────┬───────────────────────────────┬───────────────────────────────┬─────────────┘
            │                               │                               │
┌───────────▼─────────────┐     ┌───────────▼─────────────┐     ┌───────────▼─────────────┐
│    MEMBER 3: REPO &     │     │     MEMBER 4: TASK      │     │  MEMBER 5: VERIFY &     │
│       MEMORY LEAD       │     │     ORCHESTRATOR        │     │     BENCHMARK LEAD      │
│ (backend/repo_memory/)  │     │ (backend/orchestrator/) │     │ (backend/verification/) │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

### Detailed Member Specification Documents
Each member's folder structure, file specifications, exports, 24-hour phase schedule, and API boundaries are detailed in their dedicated specification files inside `Docs/`:

1. 📘 **[Member 1: Terminal CLI & TUI Lead](Member-1-CLI-Directory-Structure.md)** (`cli/`)
2. 📘 **[Member 2: Backend Core & Model Adapter Lead](Member-2-Backend-Core-Directory-Structure.md)** (`backend/core/`)
3. 📘 **[Member 3: Repo Intelligence & Tiered Memory Lead](Member-3-Repo-Memory-Directory-Structure.md)** (`backend/repo_memory/`)
4. 📘 **[Member 4: Task Orchestrator & Sandbox Security Lead](Member-4-Orchestrator-Sandbox-Directory-Structure.md)** (`backend/orchestrator/`)
5. 📘 **[Member 5: Verification, Benchmarking & Evaluation Lead](Member-5-Verification-Benchmark-Directory-Structure.md)** (`backend/verification/`)

---

## 2. Complete Repository Directory Tree

```
Billu-Gang/
├── Docs/                                       # Project Documentation Directory
│   ├── PRD.md                                  # Product Requirements Document
│   ├── Architecture.md                         # System Architecture & Design
│   ├── Tech-Stack.md                           # Languages, Frameworks & Libraries
│   ├── Frontend-Spec.md                        # Ink TUI Visual & Layout Specification
│   ├── flow.md                                 # 24-Hour Hackathon Execution Flow
│   ├── Directory-Structure.md                  # MASTER INDEX (This Document)
│   ├── Member-1-CLI-Directory-Structure.md    # Member 1 Specification
│   ├── Member-2-Backend-Core-Directory-Structure.md # Member 2 Specification
│   ├── Member-3-Repo-Memory-Directory-Structure.md  # Member 3 Specification
│   ├── Member-4-Orchestrator-Sandbox-Directory-Structure.md # Member 4 Specification
│   └── Member-5-Verification-Benchmark-Directory-Structure.md # Member 5 Specification
│
├── cli/                                        # MEMBER 1: TERMINAL CLI & TUI (Node.js / TypeScript / Ink)
│   ├── package.json
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   ├── src/
│   │   ├── index.ts                            # CLI executable entrypoint
│   │   ├── cli.ts                              # REPL runner & terminal lifecycle
│   │   ├── components/                         # Ink UI components
│   │   │   ├── Layout.tsx                      # Base grid layout container
│   │   │   ├── HeaderBar.tsx                   # Top status & cost bar
│   │   │   ├── StatusStrip.tsx                 # Footer hotkeys & state strip
│   │   │   ├── CommandLine.tsx                 # Prompt input with slash autocompletion
│   │   │   ├── ApprovalPrompt.tsx              # Safe/Unsafe execution prompt dialog [y/N]
│   │   │   └── views/                          # Main display views (5 core views)
│   │   │       ├── IntakeView.tsx              # Repo intake & AST scanning progress view
│   │   │       ├── TaskGraphView.tsx           # Interactive tree DAG view (✓ ● ○ ✗)
│   │   │       ├── DiffView.tsx                # Unified patch diff viewer (+ green / - red)
│   │   │       ├── TraceView.tsx               # Live test streaming log & OpenTelemetry view
│   │   │       ├── ReviewerSummaryView.tsx     # Patch completion proof & cost breakdown view
│   │   │       └── MemoryInspectView.tsx       # Interactive /memory tier inspection view
│   │   ├── router/
│   │   │   ├── SlashCommandRouter.ts           # Slash command router (/plan, /diff, /trace, /memory, /rollback)
│   │   │   └── commandHandlers.ts
│   │   ├── sse/
│   │   │   ├── SSEClient.ts                    # EventSource client streaming backend events
│   │   │   └── sseTypes.ts                     # Zod runtime schemas for backend events
│   │   ├── api/
│   │   │   └── BackendApiClient.ts             # Axios REST client targeting FastAPI endpoints
│   │   └── utils/
│   │       ├── formatters.ts                   # Token/cost/time formatters
│   │       └── ansi.ts                         # ANSI color & spinner helpers
│   └── tests/                                  # CLI Vitest suite
│
└── backend/                                    # Python Backend Service (Python 3.11+)
    ├── pyproject.toml                          # Poetry/Pip project configuration
    ├── alembic/                                # SQLAlchemy migration scripts
    │
    ├── core/                                   # MEMBER 2: BACKEND CORE & MODEL ADAPTER LEAD
    │   ├── main.py                             # FastAPI application factory & router mount
    │   ├── config.py                           # Application settings & environment variables
    │   ├── schemas/                            # Pydantic v2 data contracts
    │   │   ├── session.py                      # Session schemas
    │   │   ├── task_graph.py                   # Task graph node schemas
    │   │   ├── tool_call.py                    # Tool call & approval schemas
    │   │   ├── memory.py                       # Memory tier & provenance schemas
    │   │   ├── evidence.py                     # Evidence & verification schemas
    │   │   └── sse_events.py                   # SSE event schemas
    │   ├── routes/                             # FastAPI REST endpoints
    │   │   ├── session_routes.py               # /api/v1/session routes
    │   │   ├── plan_routes.py                  # /api/v1/plan routes
    │   │   ├── run_routes.py                   # /api/v1/run & /api/v1/pause routes
    │   │   ├── memory_routes.py                # /api/v1/memory routes
    │   │   ├── trace_routes.py                 # /api/v1/trace routes
    │   │   ├── rollback_routes.py              # /api/v1/rollback routes
    │   │   └── sse_routes.py                   # GET /api/v1/events (sse-starlette stream)
    │   ├── adapters/                           # Model Adapter Layer
    │   │   ├── base.py                         # Abstract Base Class ModelAdapter interface
    │   │   ├── anthropic_adapter.py            # Anthropic Claude 3.5 adapter
    │   │   ├── openai_adapter.py               # OpenAI GPT-4o adapter
    │   │   ├── mock_adapter.py                 # Offline mock adapter
    │   │   └── fallback_manager.py             # Automatic model failover manager
    │   ├── tracking/                           # Token & Cost Attribution
    │   │   ├── token_counter.py                # Tiktoken token calculator
    │   │   └── cost_tracker.py                 # USD cost tracker ($/1k tokens)
    │   └── tests/                              # Core backend unit tests
    │
    ├── repo_memory/                            # MEMBER 3: REPO INTELLIGENCE & TIERED MEMORY LEAD
    │   ├── db/                                 # Storage & ORM Layer
    │   │   ├── database.py                     # SQLAlchemy SQLite engine connection
    │   │   └── models.py                       # SQLAlchemy ORM Models
    │   ├── indexer/                            # Repo Indexing Engine
    │   │   ├── ast_parser.py                   # Tree-sitter AST parser (Py/TS/JS)
    │   │   ├── symbol_graph.py                 # Symbol indexer & call graph builder (NetworkX)
    │   │   ├── git_inspector.py                # GitPython git blame & diff inspector
    │   │   ├── file_scanner.py                 # .gitignore-aware file scanner
    │   │   └── test_mapper.py                  # Test-to-source mapping associator
    │   ├── memory/                             # Tiered Memory Engine
    │   │   ├── tiered_store.py                 # TieredMemoryStore CRUD engine
    │   │   ├── provenance.py                   # Provenance metadata manager
    │   │   ├── invalidation.py                 # Memory auto-invalidation engine (FR11)
    │   │   └── memory_exporter.py              # Memory export/import engine (FR12)
    │   ├── context/                            # Context Manager
    │   │   ├── context_manager.py              # Token-budgeted context assembler
    │   │   ├── relevance_ranker.py             # Semantic relevance ranker (sentence-transformers)
    │   │   ├── summarizer.py                   # Hierarchical file summarizer (FR15)
    │   │   └── sanitizer.py                    # Prompt-injection & secret sanitizer (FR17)
    │   └── tests/                              # Repo & Memory unit tests
    │
    ├── orchestrator/                           # MEMBER 4: TASK ORCHESTRATOR & SANDBOX SECURITY LEAD
    │   ├── graph/                              # Task Graph & State Machine
    │   │   ├── state_graph.py                  # Async state graph runtime (LangGraph equivalent)
    │   │   ├── task_planner.py                 # Multi-step DAG task planner
    │   │   ├── replanning_engine.py            # Failure recovery & replanning engine (FR22)
    │   │   ├── agent_nodes.py                  # Specialist sub-agent nodes (planner, coder, verifier)
    │   │   ├── parallel_executor.py            # Concurrent sub-agent branch executor (FR19)
    │   │   └── checkpoints.py                  # State serialization & checkpointing
    │   ├── sandbox/                            # Docker Sandbox Service
    │   │   ├── docker_manager.py               # Docker SDK container lifecycle & volume mounts
    │   │   ├── container_exec.py               # Command execution runner inside Docker
    │   │   ├── snapshot_manager.py            # Git patch snapshotting & rollback manager
    │   │   ├── network_policy.py               # Default-deny network policy filter (NFR7, NFR8)
    │   │   └── dockerfile/
    │   │       └── Dockerfile.sandbox          # Base Docker sandbox image
    │   ├── security/                           # Safety Boundaries
    │   │   ├── approval_gate.py                # Out-of-scope command approval gate
    │   │   ├── emergency_stop.py               # SIGKILL process & abort handler (FR28)
    │   │   └── secret_redactor.py              # Log credential & token scrubber
    │   └── tests/                              # Orchestrator & Sandbox unit tests
    │
    └── verification/                           # MEMBER 5: VERIFICATION, BENCHMARKING & EVALUATION LEAD
        ├── pipeline/                           # Verification Pipeline
        │   ├── runner.py                       # VerificationPipeline engine (build/lint/typecheck/test)
        │   ├── test_parsers.py                 # Pytest XML/JSON & npm test output parser
        │   ├── static_analyzer.py              # Ruff, ESLint & Mypy analyzer wrapper
        │   └── reviewer_engine.py              # Reviewer summary generator
        ├── trace/                              # Event Tracing
        │   ├── trace_logger.py                 # Async JSONL event tracer
        │   └── opentelemetry_config.py         # OpenTelemetry collector setup
        ├── benchmarking/                       # Benchmark Runner
        │   ├── bench_runner.py                 # Terminal-Bench & SWE-bench evaluation runner
        │   ├── issue_loader.py                 # Problem dataset loader & container feeder
        │   ├── ablation_protocol.py            # Controlled ablation execution engine (FR47)
        │   └── evaluator_grader.py            # Hidden test injection & correctness grader (FR31)
        └── tests/                              # Verification & Evaluation unit tests
```

---

## 3. High-Level Summary of Ownership by Member

| Member | Primary Directory | Core Tech Stack | Primary Responsibilities |
|---|---|---|---|
| **Member 1** | `cli/` | TypeScript, Ink, Commander.js, Vitest, Zod | Terminal CLI REPL, Ink TUI layout, 5 main pane views, slash command router, SSE client. |
| **Member 2** | `backend/core/` | Python 3.11, FastAPI, Pydantic, Anthropic SDK, OpenAI SDK, `httpx`, `sse-starlette` | FastAPI app, REST/SSE routes, pluggable model adapters, fallback switching, cost & token tracker. |
| **Member 3** | `backend/repo_memory/` | Tree-sitter, GitPython, SQLite (SQLAlchemy), sentence-transformers, tiktoken, NetworkX | Polyglot AST symbol indexer, call graph, SQLite 7-tier memory store, provenance, context manager. |
| **Member 4** | `backend/orchestrator/` | LangGraph / State Graph, Docker SDK (`docker-py`), Asyncio, Git snapshotting | Task graph DAG planner, Docker sandbox container manager, dynamic replanning, approval gates, SIGKILL abort. |
| **Member 5** | `backend/verification/` | Pytest, OpenTelemetry, Terminal-Bench, SWE-bench, ESLint, Mypy, Ruff | Verification pipeline (build/lint/test), JSONL trace logger, benchmark runner, ablation protocol, reviewer summary. |

---

## 4. Cross-Member Interface Contracts & Guidelines

1. **CLI ↔ Backend REST & SSE:** CLI (`cli/src/api/` & `cli/src/sse/`) communicates with FastAPI (`backend/core/routes/`) exclusively via HTTP REST endpoints and `sse-starlette` SSE payloads validated by Pydantic schemas in `backend/core/schemas/` and Zod schemas in `cli/src/sse/sseTypes.ts`.
2. **Orchestrator ↔ Model Adapter:** Orchestrator (`backend/orchestrator/`) requests LLM completions ONLY through `ModelAdapter` (`backend/core/adapters/base.py`). Direct provider SDK calls inside orchestrator nodes are prohibited.
3. **Orchestrator ↔ Sandbox Execution:** No commands run directly on the host machine. All code modifications and shell commands MUST run inside `DockerSandbox` (`backend/orchestrator/sandbox/container_exec.py`).
4. **Orchestrator ↔ Verification:** Verification pipeline (`backend/verification/pipeline/runner.py`) is triggered after every code edit inside sandbox. Tasks are marked complete ONLY on test proof returned by Member 5's pipeline.
5. **Context Manager ↔ Tiered Memory:** Context Manager (`backend/repo_memory/context/context_manager.py`) queries SQLite Tiered Memory (`backend/repo_memory/memory/tiered_store.py`) to assemble dynamic prompts matching model token limits.

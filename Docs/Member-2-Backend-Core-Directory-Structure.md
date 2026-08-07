# Member 2 — Backend Core & Model Adapter Lead: Directory Structure & File Specification

## 1. Overview & Ownership Domain
- **Member:** Member 2
- **Primary Role:** Backend Core & Model Adapter Lead
- **Engineering Surfaces Owned:** Model Adapter Layer, FastAPI Server Infrastructure, Token & Cost Attribution
- **Tech Stack & Tools:** Python 3.11, FastAPI, Pydantic v2, Anthropic SDK, OpenAI SDK, `httpx`, `sse-starlette`, `tiktoken`
- **Primary Root Location:** `backend/core/`

---

## 2. Dedicated Directory Tree

```
backend/core/
├── __init__.py                         # Package initializer
├── main.py                             # FastAPI application factory, middleware, CORS & router registration
├── config.py                           # Application settings & environment variables (pydantic-settings)
│
├── schemas/                            # Pydantic v2 Input/Output Schemas (API Data Contracts)
│   ├── __init__.py
│   ├── session.py                      # Session, SessionCreate, SessionResponse schemas
│   ├── task_graph.py                   # TaskGraphNode, NodeStatus, TaskType schemas
│   ├── tool_call.py                    # ToolCall, CommandScope, ApprovalRequest schemas
│   ├── memory.py                       # MemoryItem, MemoryTier enum, ProvenanceMetadata schemas
│   ├── evidence.py                     # EvidenceRecord, VerificationRun schemas
│   └── sse_events.py                   # SSE Event schemas (plan_updated, tool_started, test_finished)
│
├── routes/                             # FastAPI REST & SSE Route Handlers
│   ├── __init__.py
│   ├── session_routes.py               # /api/v1/session (create, retrieve, status)
│   ├── plan_routes.py                  # /api/v1/plan (get task graph, trigger replan)
│   ├── run_routes.py                   # /api/v1/run (start execution, pause, resume)
│   ├── memory_routes.py                # /api/v1/memory (CRUD, filter by tier, export, wipe)
│   ├── trace_routes.py                 # /api/v1/trace (retrieve event log, JSONL stream)
│   ├── rollback_routes.py              # /api/v1/rollback (trigger workspace rollback)
│   └── sse_routes.py                   # GET /api/v1/events (sse-starlette Broadcaster endpoint)
│
├── adapters/                           # Pluggable Model Adapter Layer
│   ├── __init__.py
│   ├── base.py                         # Abstract Base Class ModelAdapter interface
│   ├── anthropic_adapter.py            # Anthropic Python SDK implementation (Claude 3.5 Sonnet / Haiku)
│   ├── openai_adapter.py               # OpenAI Python SDK implementation (GPT-4o / GPT-4o-mini)
│   ├── mock_adapter.py                 # Offline mock adapter for zero-cost testing
│   └── fallback_manager.py             # Automatic model switching on rate-limits / timeout / provider outages
│
├── tracking/                           # Token & Cost Attribution Engine
│   ├── __init__.py
│   ├── token_counter.py                # Tiktoken token calculator for input/output prompts
│   └── cost_tracker.py                 # Real-time USD cost accumulator ($/1k tokens per model)
│
└── tests/                              # Unit & Integration Tests for Backend Core
    ├── __init__.py
    ├── test_routes.py                  # FastAPI REST endpoints unit tests
    ├── test_adapters.py                # Model adapter interface & provider payload translation tests
    ├── test_fallback_manager.py        # Automatic provider failover tests
    ├── test_cost_tracker.py            # Cost and token attribution unit tests
    └── test_sse_broadcaster.py         # SSE streaming event broadcaster tests
```

---

## 3. Detailed File Responsibilities & Key Exports

| File Path | Purpose & Responsibilities | Key Functions / Classes / Components |
|---|---|---|
| `backend/core/main.py` | FastAPI app creation, startup/shutdown events, CORS configuration, exception handlers. | `app = FastAPI()`, `get_application()` |
| `backend/core/config.py` | Environment variable management (API Keys, Server Port, Log Level, Max Budget). | `class Settings(BaseSettings)` |
| `backend/core/schemas/session.py` | Defines session request/response structures matching Architecture spec. | `class Session`, `class SessionCreate` |
| `backend/core/schemas/task_graph.py` | Typed model for Task Graph Nodes and parent-child DAG relations. | `class TaskGraphNode`, `class NodeStatus` |
| `backend/core/schemas/tool_call.py` | Defines tool invocation requests, arguments, and execution responses. | `class ToolCall`, `class ApprovalRequest` |
| `backend/core/schemas/memory.py` | Memory item payload definition with required provenance and invalidation fields. | `class MemoryItem`, `enum MemoryTier` |
| `backend/core/schemas/sse_events.py` | Data structure for SSE events pushed live to the CLI. | `class SSEEvent`, `enum EventType` |
| `backend/core/routes/session_routes.py` | Endpoints to create, query, and close harness coding sessions. | `POST /session`, `GET /session/{id}` |
| `backend/core/routes/plan_routes.py` | Endpoints to fetch active task DAG and request plan modifications. | `GET /plan`, `POST /plan/replan` |
| `backend/core/routes/run_routes.py` | Trigger harness autonomous run, pause execution, or cancel active tasks. | `POST /run`, `POST /pause` |
| `backend/core/routes/rollback_routes.py` | Reverts sandbox repository state to initial or checkpoint patch. | `POST /rollback` |
| `backend/core/routes/sse_routes.py` | Broadcaster endpoint using `sse-starlette` streaming live updates to Ink CLI. | `GET /events` (`EventSourceResponse`) |
| `backend/core/adapters/base.py` | Abstract Base Class defining `complete()`, `stream_complete()`, and `get_token_count()`. | `class ModelAdapter(ABC)` |
| `backend/core/adapters/anthropic_adapter.py` | Anthropic SDK wrapper handling messages API, system prompts, and tool calling schemas. | `class AnthropicAdapter(ModelAdapter)` |
| `backend/core/adapters/openai_adapter.py` | OpenAI SDK wrapper handling chat completions and structured outputs. | `class OpenAIAdapter(ModelAdapter)` |
| `backend/core/adapters/fallback_manager.py` | Dynamically switches from primary adapter (e.g. Anthropic) to secondary (e.g. OpenAI) on error. | `class FallbackAdapterManager` |
| `backend/core/tracking/token_counter.py` | Counts prompt and completion tokens using `tiktoken` for precise context budgeting. | `count_tokens(text, model)` |
| `backend/core/tracking/cost_tracker.py` | Calculates cumulative USD cost based on token counts and model pricing tables. | `class CostTracker`, `calculate_cost()` |

---

## 4. 24-Hour Phase Deliverables Schedule

```
Phase 1 (H0-H3) ──► Phase 2 (H3-H8) ──► Phase 3 (H8-H13) ──► Phase 4 (H13-H17) ──► Phase 5 (H17-H21) ──► Phase 6 (H21-H24)
  FastAPI Skeleton &   Model Adapters &     Wire Adapter to       Provider Fallback &   Model Swap Verification Security Audit &
  Pydantic Schemas     Cost/Token Tracker   Orchestrator + SSE    Session Persistence   & Cost Report          OpenAPI Spec Freeze
```

1. **Phase 1 (Hours 0–3):**
   - Initialize FastAPI application skeleton and folder hierarchy under `backend/core/`.
   - Freeze core Pydantic v2 schemas: `Session`, `TaskGraphNode`, `ToolCall`, `MemoryItem`, `EvidenceRecord`, `VerificationRun`.
   - Build SSE event broadcaster (`sse-starlette`) and endpoint stubs (`/session`, `/plan`, `/run`).
2. **Phase 2 (Hours 3–8):**
   - Build `ModelAdapter` abstract base class and concrete adapters (`AnthropicAdapter`, `OpenAIAdapter`).
   - Implement prompt formatting and tool-calling schema translation for Claude 3.5 & GPT-4o.
   - Implement `token_counter.py` (`tiktoken`) and `cost_tracker.py` ($/1k tokens).
3. **Phase 3 (Hours 8–13):**
   - Wire `ModelAdapter` completions directly to Orchestrator's tool dispatch loop.
   - Stream real-time events (`plan_updated`, `tool_started`, `tool_finished`, `verification_started`, `verification_finished`).
   - Implement `/api/v1/rollback` endpoint.
4. **Phase 4 (Hours 13–17):**
   - Build `fallback_manager.py` for automatic provider failover on API rate-limits or outages.
   - Implement session state serialization and resume mechanism.
   - Refine API error handling to prevent backend crashes on malformed LLM responses.
5. **Phase 5 (Hours 17–21):**
   - Run model independence verification: execute benchmark suite switching adapters with zero harness code changes.
   - Generate total token usage, wall-clock latency, and financial cost summary report.
6. **Phase 6 (Hours 21–24):**
   - Perform security audit: ensure no API keys or local host credentials leak into traces or memory DBs.
   - Finalize FastAPI OpenAPI documentation (`/docs`).

---

## 5. Subsystem Dependencies & API Boundaries
- **Backend Core ↔ Model Providers:** Direct HTTP calls using `httpx` / official Anthropic & OpenAI SDKs inside `adapters/`.
- **Backend Core ↔ Orchestrator:** Provides `ModelAdapter` interface to `TaskGraphOrchestrator` for generating plans and patches.
- **Backend Core ↔ CLI:** Exposes OpenAPI REST endpoints and `sse-starlette` stream broadcast.

---

## 6. Completed Implementation Summary (Phases 1 to 4)

### Phase 1 (Hours 0–3): FastAPI Skeleton & Pydantic Schemas
- **FastAPI Core (`backend/core/main.py`, `config.py`):** Configured application factory with CORS middleware, health check endpoint (`/health`), and `/api/v1` route mounting.
- **Pydantic v2 Schemas (`backend/core/schemas/`):** Implemented input/output models: `Session`, `SessionCreate`, `TaskGraphNode`, `ToolCall`, `MemoryItem`, `EvidenceRecord`, `SSEEvent`.
- **REST Route Stubs (`backend/core/routes/`):** Established routers for session, plan, run, memory, trace, rollback, and SSE endpoints.

### Phase 2 (Hours 3–8): LangChain & LangGraph Adapters & Token/Cost Engine
- **Model Adapter Layer (`backend/core/adapters/`):**
  - Built `ModelAdapter` ABC with `ToolCallData` extraction and message converters.
  - Implemented `LangChainAdapter` leveraging LangChain `BaseChatModel`, tool schema binding (`bind_tools`), and async streaming (`astream`).
  - Implemented `LangGraphAdapter` using LangGraph `StateGraph` with `planner`, `executor`, and `verifier` nodes.
  - Enhanced `MockAdapter` for zero-cost offline harness testing.
- **Token & Cost Engine (`backend/core/tracking/`):**
  - Implemented `token_counter.py` supporting single string text and complete message lists (`count_tokens_for_messages`) using `tiktoken`.
  - Built `CostTracker` with USD pricing tables ($/1k tokens), usage log records, budget limit checks, and warning threshold alerts (`is_warning_threshold_reached`).

### Phase 3 (Hours 8–13): Execution Loop Wiring, SSE Queue & Rollback Endpoint
- **Execution Loop Wiring (`backend/core/routes/plan_routes.py`, `run_routes.py`):** Wired `LangGraphAdapter` to generate task graph DAGs on `/api/v1/plan` and `/api/v1/plan/replan`. Wired `LangChainAdapter` model completions to `/api/v1/run/start`.
- **PubSub SSE Event Queue (`backend/core/routes/sse_routes.py`):** Implemented `SSEBroadcaster` with `asyncio.Queue` event subscription/publishing for live CLI streaming (`plan_updated`, `tool_started`, `tool_finished`, `cost_updated`).
- **Workspace Rollback Endpoint (`backend/core/routes/rollback_routes.py`):** Implemented `/api/v1/rollback` handling target checkpoint selection, patch reversal triggers, and status verification notifications.

### Phase 4 (Hours 13–17): Provider Fallback, Session Persistence & Error Recovery
- **Automatic Provider Failover (`backend/core/adapters/fallback_manager.py`):** Enhanced `FallbackAdapterManager` with automatic multi-tier failover (Primary LLM -> Secondary LLM -> Mock Adapter), logging failover records, and broadcasting `error_occurred` / `fallback_triggered` SSE events.
- **Session State Persistence & Resumption (`backend/core/schemas/session.py`, `session_routes.py`):** Added `SessionStateCheckpoint` schema and endpoints: `POST /api/v1/session/{session_id}/resume` and `GET /api/v1/session/{session_id}/export`.
- **Robust Exception Handlers (`backend/core/main.py`):** Configured custom FastAPI exception handlers returning standardized JSON error responses to prevent backend crashes on malformed LLM outputs or rate limits.
- **Phase 4 Unit Test Suite (`backend/core/tests/`):** Added unit test coverage for provider failover scenarios (`test_fallback_manager.py`) and session export/resume endpoints (`test_routes.py`).



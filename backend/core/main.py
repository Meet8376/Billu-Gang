"""
FastAPI Application Factory, OpenAPI Specification, Middleware, Router Registration & Exception Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.routes import (
    session_routes,
    plan_routes,
    run_routes,
    memory_routes,
    trace_routes,
    rollback_routes,
    sse_routes,
    security_routes,
)

# Comprehensive OpenAPI Tag Descriptions
OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "System health check and operational status endpoints.",
    },
    {
        "name": "Session",
        "description": "Lifecycle management for autonomous coding sessions, state checkpoints, export, and resumption.",
    },
    {
        "name": "Plan",
        "description": "Task graph generation, DAG node orchestration, and dynamic replanning via LangGraph adapters.",
    },
    {
        "name": "Run",
        "description": "Execution control loop (start, pause, resume, cancel) for model adapter tool dispatches.",
    },
    {
        "name": "Memory",
        "description": "Tiered memory system (Short-term working, Medium-term session, Long-term repo knowledge) with automatic security credential redaction.",
    },
    {
        "name": "Trace",
        "description": "Event trace logging, zero-harness-change model swap benchmarks, and financial USD token cost reporting.",
    },
    {
        "name": "Rollback",
        "description": "Workspace safety rollback engine for checkpoint state recovery and patch reversal.",
    },
    {
        "name": "Events",
        "description": "Real-time Server-Sent Events (SSE) stream broadcast for live CLI user interfaces.",
    },
    {
        "name": "Security",
        "description": "Security audit scanning, API key redaction engine, and leak verification endpoints.",
    },
]

API_DESCRIPTION = """
# AE-01 Unified Agentic Coding Harness — Backend Core Engine

Welcome to the **AE-01 Backend Core Engine** documentation. This service powers the autonomous coding harness, coordinating model adapters, task graph orchestrators, tiered memory, workspace rollback systems, and financial cost accounting.

---

### Key Subsystems & Features:
1. **Model Adapter Layer (`adapters/`):** Unified `ModelAdapter` interface supporting `LangChainAdapter`, `LangGraphAdapter`, and `MockAdapter` with multi-tier fallback management.
2. **Token & Cost Attribution Engine (`tracking/`):** Real-time token usage counting, wall-clock latency tracking, and financial USD summary generation against budget guardrails.
3. **Session Persistence & State Checkpoints (`routes/session_routes.py`):** Serializable session snapshotting (`SessionStateCheckpoint`), workspace exports, and seamless session resumption.
4. **Model Independence Verification (`routes/trace_routes.py`):** Swap LLMs (e.g. GPT-4o, Claude 3.5 Sonnet, Mock) with zero harness code modifications.
5. **Tiered Memory System (`routes/memory_routes.py`):** Short-term, Medium-term, and Long-term context storage with invalidation support.
6. **Workspace Safety Rollback (`routes/rollback_routes.py`):** Transactional workspace state rollback to prior session checkpoints.
7. **Security Credential Audit & Redaction (`security.py` & `routes/security_routes.py`):** Regex-based redactor preventing API keys (OpenAI, Anthropic, GitHub), passwords, bearer tokens, or local credentials from leaking into trace logs, memory stores, or API responses.
8. **Real-Time SSE Event Broadcasting (`routes/sse_routes.py`):** Asynchronous event streaming to CLI TUI clients.
"""


def get_application() -> FastAPI:
    """Create and configure FastAPI application instance with finalized OpenAPI documentation."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        summary="AE-01 Autonomous Coding Harness Backend Core Engine",
        description=API_DESCRIPTION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=OPENAPI_TAGS,
        contact={
            "name": "Member 2 — Backend Core & Model Adapter Lead",
            "url": "https://github.com/Meet8376/Billu-Gang",
        },
        license_info={
            "name": "MIT License",
        },
    )

    # Configure CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Custom Exception Handlers to Prevent Backend Crashes
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid Value", "detail": str(exc)},
        )

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request: Request, exc: RuntimeError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "Model Provider Runtime Error", "detail": str(exc)},
        )

    # Register Routers under /api/v1
    app.include_router(session_routes.router, prefix="/api/v1", tags=["Session"])
    app.include_router(plan_routes.router, prefix="/api/v1", tags=["Plan"])
    app.include_router(run_routes.router, prefix="/api/v1", tags=["Run"])
    app.include_router(memory_routes.router, prefix="/api/v1", tags=["Memory"])
    app.include_router(trace_routes.router, prefix="/api/v1", tags=["Trace"])
    app.include_router(rollback_routes.router, prefix="/api/v1", tags=["Rollback"])
    app.include_router(sse_routes.router, prefix="/api/v1", tags=["Events"])
    app.include_router(security_routes.router, prefix="/api/v1", tags=["Security"])

    @app.get("/health", tags=["Health"], summary="System Health Check")
    async def health_check():
        """Check status and health of Backend Core engine."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    return app


app = get_application()

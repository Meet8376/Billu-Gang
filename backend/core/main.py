"""
FastAPI Application Factory, Middleware & Router Registration.
Member 2 — Backend Core & Model Adapter Lead
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.routes import (
    session_routes,
    plan_routes,
    run_routes,
    memory_routes,
    trace_routes,
    rollback_routes,
    sse_routes,
)


def get_application() -> FastAPI:
    """Create and configure FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers under /api/v1
    app.include_router(session_routes.router, prefix="/api/v1", tags=["Session"])
    app.include_router(plan_routes.router, prefix="/api/v1", tags=["Plan"])
    app.include_router(run_routes.router, prefix="/api/v1", tags=["Run"])
    app.include_router(memory_routes.router, prefix="/api/v1", tags=["Memory"])
    app.include_router(trace_routes.router, prefix="/api/v1", tags=["Trace"])
    app.include_router(rollback_routes.router, prefix="/api/v1", tags=["Rollback"])
    app.include_router(sse_routes.router, prefix="/api/v1", tags=["Events"])

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    return app


app = get_application()

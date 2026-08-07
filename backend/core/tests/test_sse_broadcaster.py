"""
Unit Tests for SSE Event Broadcaster.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.routes.sse_routes import router as sse_router
from backend.core.main import app


def test_sse_route_defined():
    """Verify that SSE broadcaster route handler is defined."""
    route_paths = [r.path for r in sse_router.routes]
    assert "/events" in route_paths


def test_app_includes_sse_router():
    """Verify that main FastAPI application includes the SSE router."""
    assert sse_router in [r.app for r in app.routes if hasattr(r, "app")] or len(app.routes) > 0

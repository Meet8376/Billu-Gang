"""
Unit Tests for SSE Event Broadcaster.
Member 2 — Backend Core & Model Adapter Lead
"""

from fastapi.testclient import TestClient
from backend.core.main import app

client = TestClient(app)


def test_sse_endpoint_exists():
    # SSE route endpoint check
    response = client.get("/api/v1/events")
    # SSE endpoints respond with continuous stream headers (200 OK)
    assert response.status_code == 200

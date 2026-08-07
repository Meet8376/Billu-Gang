"""
Unit Tests for FastAPI REST Endpoints.
Member 2 — Backend Core & Model Adapter Lead
"""

from fastapi.testclient import TestClient
from backend.core.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_session():
    payload = {
        "workspace_path": "/tmp/test-workspace",
        "goal_prompt": "Fix bug in calculation module",
        "max_budget_usd": 5.0,
    }
    response = client.post("/api/v1/session", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "idle"


def test_run_control_endpoints():
    payload = {"session_id": "test-session-123"}
    resp = client.post("/api/v1/run/start", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"

"""
Phase 4 Unit Tests for FastAPI REST Endpoints & Session Persistence.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
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


def test_export_and_resume_session():
    # 1. Create session
    payload = {
        "workspace_path": "/tmp/test-workspace-persisted",
        "goal_prompt": "Persistence test prompt",
        "max_budget_usd": 10.0,
    }
    create_resp = client.post("/api/v1/session", json=payload)
    session_id = create_resp.json()["session_id"]

    # 2. Export session checkpoint
    export_resp = client.get(f"/api/v1/session/{session_id}/export")
    assert export_resp.status_code == 200
    checkpoint = export_resp.json()
    assert checkpoint["session_id"] == session_id
    assert "checkpoint_id" in checkpoint

    # 3. Resume session
    resume_payload = {"session_id": session_id, "checkpoint_id": checkpoint["checkpoint_id"]}
    resume_resp = client.post(f"/api/v1/session/{session_id}/resume", json=resume_payload)
    assert resume_resp.status_code == 200
    resumed = resume_resp.json()
    assert resumed["session_id"] == session_id
    assert resumed["status"] == "running"


def test_get_plan_endpoint():
    response = client.get("/api/v1/plan/sess_test_123")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "sess_test_123"
    assert "nodes" in data


def test_replan_endpoint():
    payload = {"session_id": "sess_test_123", "feedback": "Add error handling"}
    response = client.post("/api/v1/plan/replan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "sess_test_123"
    assert len(data["nodes"]) > 0


def test_run_start_endpoint():
    payload = {"session_id": "test-session-123"}
    resp = client.post("/api/v1/run/start", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"


def test_rollback_endpoint():
    payload = {"session_id": "sess_test_123", "target_checkpoint_id": "chk_001"}
    response = client.post("/api/v1/rollback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["target_checkpoint_id"] == "chk_001"

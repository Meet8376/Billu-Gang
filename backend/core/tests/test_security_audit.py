"""
Phase 6 Unit Tests for Security Credential Redaction, Security Auditor & Security REST API Endpoints.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from fastapi.testclient import TestClient
from backend.core.main import app
from backend.core.security import CredentialSanitizer, SecurityAuditor
from backend.core.schemas.memory import MemoryItem, MemoryTier

client = TestClient(app)


def test_credential_sanitizer_openai_key():
    raw_text = "Connecting to OpenAI with key sk-proj-1234567890abcdef1234567890abcdef in session."
    clean_text, count = CredentialSanitizer.sanitize_text(raw_text)
    assert count == 1
    assert "sk-proj-" not in clean_text
    assert "[REDACTED_OPENAI_KEY]" in clean_text


def test_credential_sanitizer_anthropic_key():
    raw_text = "Anthropic adapter key sk-ant-api03-abcdef1234567890abcdef1234567890 initialized."
    clean_text, count = CredentialSanitizer.sanitize_text(raw_text)
    assert count == 1
    assert "sk-ant-api03-" not in clean_text
    assert "[REDACTED_ANTHROPIC_KEY]" in clean_text


def test_credential_sanitizer_github_token():
    raw_text = "Git auth token ghp_123456789012345678901234567890123456 used for push."
    clean_text, count = CredentialSanitizer.sanitize_text(raw_text)
    assert count == 1
    assert "ghp_" not in clean_text
    assert "[REDACTED_GITHUB_TOKEN]" in clean_text


def test_credential_sanitizer_bearer_token():
    raw_text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abcdef"
    clean_text, count = CredentialSanitizer.sanitize_text(raw_text)
    assert count == 1
    assert "[REDACTED_BEARER_TOKEN]" in clean_text


def test_credential_sanitizer_sensitive_dict_keys():
    payload = {
        "user": "test_user",
        "api_key": "secret_key_12345",
        "password": "SuperSecretPassword123!",
        "config": {"nested_key": "sk-proj-999999999999999999999999"},
    }
    sanitized, count = CredentialSanitizer.sanitize_payload(payload)
    assert count >= 3
    assert sanitized["api_key"] == "[REDACTED_API_KEY]"
    assert sanitized["password"] == "[REDACTED_PASSWORD]"
    assert "[REDACTED_OPENAI_KEY]" in sanitized["config"]["nested_key"]


def test_security_auditor_clean_report():
    clean_memory = [
        MemoryItem(id="m1", tier=MemoryTier.SHORT_TERM, content="Clean session summary")
    ]
    clean_traces = [{"session_id": "s1", "message": "Normal execution step"}]

    report = SecurityAuditor.run_full_audit(memory_items=clean_memory, trace_logs=clean_traces)
    assert report.clean is True
    assert report.leaks_detected_count == 0
    assert "PASSED" in report.audit_summary


def test_security_auditor_detects_leaks():
    leaky_memory = [
        MemoryItem(id="m2", tier=MemoryTier.LONG_TERM, content="Leaked key: sk-ant-api03-1234567890abcdef12345678")
    ]
    report = SecurityAuditor.run_full_audit(memory_items=leaky_memory, trace_logs=[])
    assert report.clean is False
    assert report.leaks_detected_count >= 1
    assert report.leak_details[0].leak_type == "Anthropic API Key"


def test_security_audit_api_endpoint():
    response = client.get("/api/v1/security/audit")
    assert response.status_code == 200
    data = response.json()
    assert "clean" in data
    assert "total_items_scanned" in data
    assert "audit_summary" in data


def test_security_sanitize_api_endpoint():
    payload = {
        "text": "Call OpenAI with sk-proj-111122223333444455556666",
        "payload": {"secret": "my_db_password_123"},
    }
    response = client.post("/api/v1/security/sanitize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["original_has_leaks"] is True
    assert "[REDACTED_OPENAI_KEY]" in data["sanitized_text"]
    assert data["sanitized_payload"]["secret"] == "[REDACTED_SECRET]"


def test_memory_auto_sanitization():
    item_payload = {
        "id": "mem_sec_test",
        "tier": "short_term",
        "content": "Storing Anthropic key sk-ant-api03-999988887777666655554444 in memory.",
    }
    create_resp = client.post("/api/v1/memory", json=item_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert "sk-ant-api03" not in created["content"]
    assert "[REDACTED_ANTHROPIC_KEY]" in created["content"]


def test_trace_auto_sanitization():
    trace_payload = {
        "session_id": "sess_sec_test",
        "timestamp": "2026-08-07T12:00:00Z",
        "log_level": "INFO",
        "message": "Trace log containing ghp_123456789012345678901234567890123456 key.",
    }
    create_resp = client.post("/api/v1/trace", json=trace_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert "ghp_" not in created["message"]
    assert "[REDACTED_GITHUB_TOKEN]" in created["message"]

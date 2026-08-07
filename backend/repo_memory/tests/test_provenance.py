"""
Unit tests for Provenance Management (memory/provenance.py)
"""

from backend.repo_memory.memory.provenance import (
    create_provenance_record,
    validate_provenance,
    ProvenanceRecord,
)


def test_create_provenance_record():
    record = create_provenance_record(
        source_file="auth/login.py",
        source_line=42,
        created_by="gpt-4o",
        confidence=0.95,
        meta={"key": "value"}
    )
    assert record["source_file"] == "auth/login.py"
    assert record["source_line"] == 42
    assert record["created_by"] == "gpt-4o"
    assert record["confidence"] == 0.95
    assert record["meta"] == {"key": "value"}
    assert "timestamp" in record


def test_validate_provenance():
    valid = {"confidence": 0.8, "source_file": "test.py"}
    assert validate_provenance(valid) is True
    
    invalid_confidence = {"confidence": 1.5}
    assert validate_provenance(invalid_confidence) is False

    invalid_type = "not a dict"
    assert validate_provenance(invalid_type) is False

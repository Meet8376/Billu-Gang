"""
Evidence & Verification Pydantic v2 Schemas.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    TEST_LOG = "test_log"
    BUILD_OUTPUT = "build_output"
    STATIC_ANALYSIS = "static_analysis"
    MANUAL_INSPECTION = "manual_inspection"


class EvidenceRecord(BaseModel):
    """Container for recorded verification evidence."""
    id: str
    evidence_type: EvidenceType
    command: str
    exit_code: int
    stdout: str
    stderr: str
    passed: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VerificationRun(BaseModel):
    """Container for a full verification run suite."""
    run_id: str
    session_id: str
    records: List[EvidenceRecord] = Field(default_factory=list)
    all_passed: bool = False
    duration_seconds: float = 0.0

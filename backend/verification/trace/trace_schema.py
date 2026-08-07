"""
Standardized JSONL Event Trace Schema Definitions.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class TraceEventType(str, Enum):
    """Supported event trace types in the agentic harness."""
    PLAN_REVISED = "plan_revised"
    TOOL_CALLED = "tool_called"
    TOOL_COMPLETED = "tool_completed"
    TEST_RUN_STARTED = "test_run_started"
    TEST_RUN_COMPLETED = "test_run_completed"
    TOKEN_USAGE_LOGGED = "token_usage_logged"
    ERROR_OCCURRED = "error_occurred"
    VERIFICATION_STEP = "verification_step"


class TraceEvent(BaseModel):
    """Standardized JSONL Event Record for structured tracing."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for trace event")
    session_id: str = Field(..., description="Coding session ID associated with this trace event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of event occurrence")
    event_type: TraceEventType = Field(..., description="Categorized event type")
    actor: str = Field("system", description="Subsystem or actor generating event (e.g. orchestrator, verification_runner)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload dictionary")
    token_cost_usd: float = Field(0.0, description="Financial USD cost attributed to this event step")
    duration_ms: float = Field(0.0, description="Execution duration in milliseconds")

    def to_jsonl_line(self) -> str:
        """Serialize trace event to a single-line JSON string (JSONL format)."""
        data = self.model_dump(mode="json")
        return json.dumps(data, separators=(",", ":")) + "\n"

    @classmethod
    def from_jsonl_line(cls, line: str) -> "TraceEvent":
        """Parse a single JSONL line string into a TraceEvent instance."""
        raw = json.loads(line.strip())
        return cls.model_validate(raw)

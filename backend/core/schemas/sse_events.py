"""
SSE Event Pydantic v2 Schemas for Real-Time Execution Pipeline.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class EventType(str, Enum):
    # Pipeline Execution Stages
    CLONE_STARTED = "clone_started"
    CLONE_COMPLETED = "clone_completed"
    DETECTION_STARTED = "detection_started"
    DETECTION_COMPLETED = "detection_completed"
    CONTAINER_STARTED = "container_started"
    DEPENDENCY_INSTALL_STARTED = "dependency_install_started"
    DEPENDENCY_INSTALL_COMPLETED = "dependency_install_completed"
    TESTS_STARTED = "tests_started"
    TESTS_COMPLETED = "tests_completed"
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    REPORT_STARTED = "report_started"
    REPORT_COMPLETED = "report_completed"
    PATCH_APPLIED = "patch_applied"
    EXECUTION_FAILED = "execution_failed"


    # Legacy & Auxiliary Events
    PLAN_UPDATED = "plan_updated"
    TOOL_STARTED = "tool_started"
    TOOL_FINISHED = "tool_finished"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_FINISHED = "verification_finished"
    MEMORY_UPDATED = "memory_updated"
    COST_UPDATED = "cost_updated"
    ERROR_OCCURRED = "error_occurred"
    LOG_LINE = "log_line"


class SSEEvent(BaseModel):
    """Structure for live SSE events pushed to CLI client."""
    event_id: str
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stage_name: Optional[str] = None
    completed_stages: Optional[int] = 0
    total_stages: Optional[int] = 7
    progress_percentage: Optional[float] = 0.0
    log_line: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)

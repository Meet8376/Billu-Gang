"""
SSE Event Pydantic v2 Schemas.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    PLAN_UPDATED = "plan_updated"
    TOOL_STARTED = "tool_started"
    TOOL_FINISHED = "tool_finished"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_FINISHED = "verification_finished"
    MEMORY_UPDATED = "memory_updated"
    COST_UPDATED = "cost_updated"
    ERROR_OCCURRED = "error_occurred"


class SSEEvent(BaseModel):
    """Structure for live SSE events pushed to CLI client."""
    event_id: str
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(default_factory=dict)

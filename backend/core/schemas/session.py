"""
Session Pydantic v2 Schemas.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionCreate(BaseModel):
    """Payload to initialize a coding session."""
    workspace_path: str = Field(..., description="Absolute local path to workspace directory")
    goal_prompt: str = Field(..., description="High level task goal prompt from user")
    max_budget_usd: Optional[float] = Field(default=10.0, description="Max USD budget for this session")


class SessionResponse(BaseModel):
    """Response returned upon session creation or query."""
    session_id: str
    workspace_path: str
    goal_prompt: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0


class Session(BaseModel):
    """Internal complete session model."""
    id: str
    workspace_path: str
    goal_prompt: str
    status: SessionStatus = SessionStatus.IDLE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0

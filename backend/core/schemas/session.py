"""
Session Pydantic v2 Schemas, Serialization Checkpoints & Benchmark Reports.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
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


class SessionStateCheckpoint(BaseModel):
    """Serializable snapshot of session state for pause/resume mechanisms."""
    checkpoint_id: str
    session_id: str
    workspace_path: str
    goal_prompt: str
    status: SessionStatus
    created_at: datetime
    saved_at: datetime = Field(default_factory=datetime.utcnow)
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    active_node_id: Optional[str] = None
    memory_snapshot_count: int = 0
    checkpoint_patch_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionResumeRequest(BaseModel):
    """Request payload to resume a serialized session checkpoint."""
    session_id: str
    checkpoint_id: Optional[str] = None
    updated_budget_usd: Optional[float] = None


class ModelBenchmarkMetrics(BaseModel):
    """Metrics recorded for an individual model adapter benchmark execution."""
    model_name: str
    tokens_input: int
    tokens_output: int
    total_tokens: int
    wall_clock_latency_seconds: float
    cost_usd: float
    success: bool
    harness_modified: bool = False


class FinancialSummaryReport(BaseModel):
    """Total session token usage, wall-clock latency, and financial USD summary report."""
    session_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost_usd: float
    total_latency_seconds: float
    max_budget_usd: float
    budget_exceeded: bool
    per_model_breakdown: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    benchmark_models_verified: List[ModelBenchmarkMetrics] = Field(default_factory=list)


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

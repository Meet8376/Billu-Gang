"""
Pydantic v2 Input/Output Schemas Package.
Member 2 — Backend Core & Model Adapter Lead
"""

from backend.core.schemas.session import (
    Session,
    SessionCreate,
    SessionResponse,
    SessionStatus,
    SessionStateCheckpoint,
    SessionResumeRequest,
)
from backend.core.schemas.task_graph import TaskGraphNode, NodeStatus, TaskType, TaskGraph
from backend.core.schemas.tool_call import ToolCall, ToolCallResult, CommandScope, ApprovalRequest, ApprovalResponse
from backend.core.schemas.memory import MemoryItem, MemoryTier, ProvenanceMetadata
from backend.core.schemas.evidence import EvidenceRecord, VerificationRun, EvidenceType
from backend.core.schemas.sse_events import SSEEvent, EventType

__all__ = [
    "Session",
    "SessionCreate",
    "SessionResponse",
    "SessionStatus",
    "SessionStateCheckpoint",
    "SessionResumeRequest",
    "TaskGraphNode",
    "NodeStatus",
    "TaskType",
    "TaskGraph",
    "ToolCall",
    "ToolCallResult",
    "CommandScope",
    "ApprovalRequest",
    "ApprovalResponse",
    "MemoryItem",
    "MemoryTier",
    "ProvenanceMetadata",
    "EvidenceRecord",
    "VerificationRun",
    "EvidenceType",
    "SSEEvent",
    "EventType",
]

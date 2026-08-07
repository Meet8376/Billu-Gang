"""
Tool Call & Approval Pydantic v2 Schemas.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CommandScope(str, Enum):
    SAFE = "safe"
    UNSAFE = "unsafe"


class ToolCall(BaseModel):
    """Payload representing a tool invocation request."""
    call_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    scope: CommandScope = CommandScope.SAFE


class ToolCallResult(BaseModel):
    """Result of a tool execution."""
    call_id: str
    tool_name: str
    success: bool
    output: str
    error: Optional[str] = None


class ApprovalRequest(BaseModel):
    """Request sent to CLI when an unsafe tool invocation requires user confirmation."""
    approval_id: str
    call_id: str
    command_str: str
    reason: str


class ApprovalResponse(BaseModel):
    """CLI user approval response."""
    approval_id: str
    approved: bool
    rejection_reason: Optional[str] = None

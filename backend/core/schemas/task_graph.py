"""
Task Graph Pydantic v2 Schemas.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class NodeStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(str, Enum):
    RESEARCH = "research"
    PLAN = "plan"
    CODE_EDIT = "code_edit"
    VERIFICATION = "verification"
    ROLLBACK = "rollback"


class TaskGraphNode(BaseModel):
    """Represents a node in the execution DAG."""
    id: str = Field(..., description="Unique node identifier")
    title: str = Field(..., description="Short node summary")
    description: Optional[str] = Field(None, description="Detailed instructions for task")
    task_type: TaskType = Field(default=TaskType.CODE_EDIT)
    status: NodeStatus = Field(default=NodeStatus.PENDING)
    parent_ids: List[str] = Field(default_factory=list, description="IDs of prerequisite nodes")
    children_ids: List[str] = Field(default_factory=list, description="IDs of dependent nodes")
    error_message: Optional[str] = None


class TaskGraph(BaseModel):
    """Complete Task Graph container."""
    session_id: str
    nodes: List[TaskGraphNode] = Field(default_factory=list)

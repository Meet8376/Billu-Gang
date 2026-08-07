"""Task Graph Planner and Node State Models (Member 4 Lead).

Constructs and manages Directed Acyclic Graphs (DAG) of sub-tasks
for issue reproduction, context search, code patching, verification, and replanning.
"""

import uuid
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"


class TaskType(str, Enum):
    REPRODUCE = "REPRODUCE"
    LOCATE = "LOCATE"
    EDIT = "EDIT"
    VERIFY = "VERIFY"
    REPLAN = "REPLAN"
    REVIEW = "REVIEW"


class TaskNode(BaseModel):
    """Represents a single node in the Task Graph DAG."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    description: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = Field(default_factory=list, description="IDs of parent nodes that must succeed before this node runs")
    result_data: Optional[Dict] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2


class TaskGraphState(BaseModel):
    """Encapsulates the complete state of a session's task graph."""
    session_id: str
    issue_description: str
    nodes: Dict[str, TaskNode] = Field(default_factory=dict)
    root_node_ids: List[str] = Field(default_factory=list)
    active_node_id: Optional[str] = None
    is_completed: bool = False
    is_failed: bool = False


class TaskPlanner:
    """Generates and updates DAG task plans for issue resolution."""

    @staticmethod
    def create_initial_plan(session_id: str, issue_description: str) -> TaskGraphState:
        """Generates initial standard engineering task DAG for an issue."""
        state = TaskGraphState(
            session_id=session_id,
            issue_description=issue_description
        )

        # Node 1: Issue Reproduction
        n1 = TaskNode(
            title="Reproduce Issue",
            description="Run reproduction test suite in sandbox to confirm baseline failure.",
            task_type=TaskType.REPRODUCE
        )

        # Node 2: Symbol & File Location
        n2 = TaskNode(
            title="Locate Target Symbols",
            description="Query repository index and call graph to locate relevant source files.",
            task_type=TaskType.LOCATE,
            dependencies=[n1.id]
        )

        # Node 3: Apply Code Patch
        n3 = TaskNode(
            title="Apply Code Edits",
            description="Generate and apply sandboxed code patch to fix identified issue.",
            task_type=TaskType.EDIT,
            dependencies=[n2.id]
        )

        # Node 4: Run Verification Suite
        n4 = TaskNode(
            title="Verify Build & Tests",
            description="Run build, linter, type-checker, and unit test suites inside sandbox.",
            task_type=TaskType.VERIFY,
            dependencies=[n3.id]
        )

        # Node 5: Reviewer Completion Report
        n5 = TaskNode(
            title="Generate Reviewer Report",
            description="Compile test evidence, cost breakdown, and rollback checkpoint.",
            task_type=TaskType.REVIEW,
            dependencies=[n4.id]
        )

        # Add nodes to state
        for n in [n1, n2, n3, n4, n5]:
            state.nodes[n.id] = n

        state.root_node_ids = [n1.id]
        state.active_node_id = n1.id
        return state

    @staticmethod
    def get_executable_nodes(state: TaskGraphState) -> List[TaskNode]:
        """Returns list of pending nodes whose dependencies have all completed successfully."""
        executable: List[TaskNode] = []

        completed_ids: Set[str] = {
            n_id for n_id, node in state.nodes.items()
            if node.status == TaskStatus.SUCCESS
        }

        for node in state.nodes.values():
            if node.status == TaskStatus.PENDING:
                # Check if all dependencies are satisfied
                if all(dep_id in completed_ids for dep_id in node.dependencies):
                    executable.append(node)

        return executable

    @staticmethod
    def update_node_status(
        state: TaskGraphState,
        node_id: str,
        status: TaskStatus,
        result_data: Optional[Dict] = None,
        error_message: Optional[str] = None
    ) -> TaskGraphState:
        """Updates status of a node and progresses active pointer."""
        if node_id not in state.nodes:
            raise KeyError(f"Task node {node_id} not found in state graph.")

        node = state.nodes[node_id]
        node.status = status
        if result_data:
            node.result_data = result_data
        if error_message:
            node.error_message = error_message

        # Determine overall completion
        if status == TaskStatus.FAILED and node.retry_count >= node.max_retries:
            state.is_failed = True

        all_completed = all(
            n.status in (TaskStatus.SUCCESS, TaskStatus.CANCELLED)
            for n in state.nodes.values()
        )
        if all_completed:
            state.is_completed = True

        # Advance active node pointer to next executable node
        next_nodes = TaskPlanner.get_executable_nodes(state)
        state.active_node_id = next_nodes[0].id if next_nodes else None

        return state

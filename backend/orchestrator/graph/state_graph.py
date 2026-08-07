"""State Graph Orchestrator Engine (Member 4 Lead).

Drives step-by-step state graph execution, status transitions,
event publishing, and checkpoint snapshot management.
"""

import logging
from typing import Awaitable, Callable, Dict, List, Optional
from backend.orchestrator.graph.task_planner import TaskGraphState, TaskNode, TaskPlanner, TaskStatus, TaskType

logger = logging.getLogger(__name__)

# Event listener signature: async (event_type: str, data: dict) -> None
EventListener = Callable[[str, Dict], Awaitable[None]]


class TaskGraphOrchestrator:
    """Async state graph engine orchestrating task node execution."""

    def __init__(self, session_id: str, repo_path: str, issue_description: str):
        self.session_id = session_id
        self.repo_path = repo_path
        self.issue_description = issue_description
        self.state: TaskGraphState = TaskPlanner.create_initial_plan(session_id, issue_description)
        self._listeners: List[EventListener] = []

    def subscribe(self, listener: EventListener) -> None:
        """Subscribes an event listener callback for SSE stream events."""
        self._listeners.append(listener)

    async def _emit_event(self, event_type: str, data: Dict) -> None:
        """Emits an event to all subscribed SSE stream listeners."""
        for listener in self._listeners:
            try:
                await listener(event_type, data)
            except Exception as e:
                logger.error(f"Error in event listener callback ({event_type}): {e}")

    def get_state(self) -> TaskGraphState:
        """Returns the current state of the task graph."""
        return self.state

    def get_graph_snapshot(self) -> Dict:
        """Returns visual snapshot dict formatted for CLI Ink TUI Task Graph View."""
        nodes_list = []
        for n_id, node in self.state.nodes.items():
            nodes_list.append({
                "id": node.id,
                "title": node.title,
                "description": node.description,
                "task_type": node.task_type.value,
                "status": node.status.value,
                "dependencies": node.dependencies,
                "is_active": (node.id == self.state.active_node_id)
            })

        return {
            "session_id": self.session_id,
            "issue": self.issue_description,
            "is_completed": self.state.is_completed,
            "is_failed": self.state.is_failed,
            "active_node_id": self.state.active_node_id,
            "nodes": nodes_list
        }

    async def execute_node_step(self, handler: Callable[[TaskNode], Awaitable[Dict]]) -> Optional[TaskNode]:
        """Executes a single step for the current active node in the graph."""
        executable_nodes = TaskPlanner.get_executable_nodes(self.state)
        if not executable_nodes:
            logger.info(f"No executable nodes available in task graph {self.session_id}")
            return None

        node = executable_nodes[0]
        self.state.active_node_id = node.id
        TaskPlanner.update_node_status(self.state, node.id, TaskStatus.IN_PROGRESS)

        await self._emit_event("node_started", {
            "session_id": self.session_id,
            "node_id": node.id,
            "title": node.title,
            "task_type": node.task_type.value
        })

        try:
            result_data = await handler(node)
            TaskPlanner.update_node_status(
                self.state,
                node.id,
                TaskStatus.SUCCESS,
                result_data=result_data
            )
            await self._emit_event("node_completed", {
                "session_id": self.session_id,
                "node_id": node.id,
                "status": TaskStatus.SUCCESS.value,
                "result": result_data
            })
            return node
        except Exception as e:
            logger.error(f"Task node execution failed ({node.id} - {node.title}): {e}")
            node.retry_count += 1
            status = TaskStatus.FAILED if node.retry_count >= node.max_retries else TaskStatus.PENDING

            TaskPlanner.update_node_status(
                self.state,
                node.id,
                status,
                error_message=str(e)
            )

            await self._emit_event("node_failed", {
                "session_id": self.session_id,
                "node_id": node.id,
                "status": status.value,
                "error": str(e),
                "retry_count": node.retry_count
            })
            return node

    async def run_until_complete(self, handler_map: Dict[TaskType, Callable[[TaskNode], Awaitable[Dict]]]) -> TaskGraphState:
        """Steps through task graph until completed, failed, or awaiting human approval."""
        while not self.state.is_completed and not self.state.is_failed:
            executable = TaskPlanner.get_executable_nodes(self.state)
            if not executable:
                break

            node = executable[0]
            handler = handler_map.get(node.task_type)
            if not handler:
                raise NotImplementedError(f"No execution handler registered for task type {node.task_type}")

            await self.execute_node_step(handler)

        return self.state

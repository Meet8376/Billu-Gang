"""Unit tests for Dynamic Replanning Engine & Self-Healing Loop (Member 4 Lead)."""

from backend.orchestrator.graph.replanning_engine import ReplanningEngine
from backend.orchestrator.graph.task_planner import TaskGraphState, TaskNode, TaskPlanner, TaskStatus, TaskType


def test_replanning_on_verification_failure():
    """Verify that ReplanningEngine injects diagnosis and fix nodes upon test failure."""
    # 1. Create initial state
    state = TaskPlanner.create_initial_plan("sess-replan-1", "Fix database connection leak")
    assert len(state.nodes) == 5

    # 2. Get verification node
    verify_nodes = [n for n in state.nodes.values() if n.task_type == TaskType.VERIFY]
    assert len(verify_nodes) == 1
    verify_node_id = verify_nodes[0].id

    # 3. Simulate failure and trigger replanning
    error_msg = "AssertionError: Expected 200 OK but got 500 Internal Server Error in test_db_connection"
    updated_state = ReplanningEngine.replan_on_failure(state, verify_node_id, error_msg)

    # 4. Assert graph modification
    assert updated_state.nodes[verify_node_id].status == TaskStatus.FAILED
    assert updated_state.nodes[verify_node_id].error_message == error_msg

    # Verify injected nodes exist
    diag_nodes = [n for n in updated_state.nodes.values() if n.task_type == TaskType.REPLAN]
    assert len(diag_nodes) == 1
    assert diag_nodes[0].id.startswith("diag-")
    assert verify_node_id in diag_nodes[0].dependencies

    # Verify active node pointer redirected to diagnosis node
    assert updated_state.active_node_id == diag_nodes[0].id
    assert updated_state.is_failed is False

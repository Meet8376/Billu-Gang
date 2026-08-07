"""Unit tests for Parallel Sub-Agent Execution Engine (FR19) (Member 4 Lead)."""

import asyncio
from backend.orchestrator.graph.parallel_executor import ParallelSubAgentExecutor
from backend.orchestrator.graph.task_planner import TaskGraphState, TaskNode, TaskStatus, TaskType


def test_parallel_sub_agent_execution():
    """Verify concurrent execution of independent DAG sub-branches (FR19)."""
    state = TaskGraphState(session_id="sess-parallel-1", issue_description="Multi-file search")

    # Create 3 independent nodes (no dependencies)
    n1 = TaskNode(id="n1", title="Branch 1", description="Search module A", task_type=TaskType.LOCATE)
    n2 = TaskNode(id="n2", title="Branch 2", description="Search module B", task_type=TaskType.LOCATE)
    n3 = TaskNode(id="n3", title="Branch 3", description="Search module C", task_type=TaskType.LOCATE)

    state.nodes = {"n1": n1, "n2": n2, "n3": n3}

    async def mock_handler(node: TaskNode):
        await asyncio.sleep(0.05)
        return {"processed": node.title}

    handler_map = {"default": mock_handler}
    executor = ParallelSubAgentExecutor(max_concurrency=3)

    results = asyncio.run(executor.run_parallel_batch(state, handler_map))

    assert len(results) == 3
    assert results["n1"]["status"] == TaskStatus.SUCCESS
    assert results["n2"]["status"] == TaskStatus.SUCCESS
    assert results["n3"]["status"] == TaskStatus.SUCCESS

"""Parallel Sub-Agent Execution Engine (Member 4 Lead).

Runs independent sub-branches of the Task Graph DAG concurrently using asyncio task pools (FR19),
optimizing throughput for independent context localization, linting, or sub-module edits.
"""

import asyncio
import logging
from typing import Awaitable, Callable, Dict, List
from backend.orchestrator.graph.task_planner import TaskGraphState, TaskNode, TaskPlanner, TaskStatus

logger = logging.getLogger(__name__)


class ParallelSubAgentExecutor:
    """Executes non-dependent Task Graph nodes concurrently using asyncio pools."""

    def __init__(self, max_concurrency: int = 4):
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def _execute_single_node(
        self,
        node: TaskNode,
        node_handler: Callable[[TaskNode], Awaitable[Dict]]
    ) -> Dict:
        """Helper to run a single node wrapped in a concurrency semaphore."""
        async with self.semaphore:
            logger.info(f"[Parallel Executor] Starting parallel branch for task '{node.id}' ({node.title})")
            node.status = TaskStatus.IN_PROGRESS
            try:
                result = await node_handler(node)
                node.status = TaskStatus.SUCCESS
                node.result_data = result
                logger.info(f"[Parallel Executor] Completed parallel branch for task '{node.id}'")
                return {"node_id": node.id, "status": TaskStatus.SUCCESS, "data": result}
            except Exception as e:
                node.status = TaskStatus.FAILED
                node.error_message = str(e)
                logger.error(f"[Parallel Executor] Failed parallel branch for task '{node.id}': {e}")
                return {"node_id": node.id, "status": TaskStatus.FAILED, "error": str(e)}

    async def run_parallel_batch(
        self,
        state: TaskGraphState,
        node_handler_map: Dict[str, Callable[[TaskNode], Awaitable[Dict]]]
    ) -> Dict[str, Dict]:
        """Identifies all executable independent DAG nodes and runs them concurrently (FR19)."""
        executable_nodes: List[TaskNode] = TaskPlanner.get_executable_nodes(state)

        if not executable_nodes:
            logger.debug("[Parallel Executor] No executable independent nodes found.")
            return {}

        logger.info(f"[Parallel Executor] Found {len(executable_nodes)} independent branches for parallel execution")

        tasks = []
        for node in executable_nodes:
            handler = node_handler_map.get(node.task_type.value) or node_handler_map.get("default")
            if not handler:
                raise ValueError(f"No handler defined for task type '{node.task_type.value}'")
            tasks.append(self._execute_single_node(node, handler))

        results_list = await asyncio.gather(*tasks)

        # Map results by node_id
        results_map = {res["node_id"]: res for res in results_list}
        return results_map

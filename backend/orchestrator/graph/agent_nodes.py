"""Specialist Agent Nodes for State Graph Execution (Member 4 Lead).

Implements planner_node, coder_node, verifier_node, and reviewer_node
connecting LLM tool calls and state graph nodes to Docker sandbox execution.
"""

import logging
from typing import Dict, Optional
from backend.orchestrator.graph.task_planner import TaskGraphState, TaskNode, TaskPlanner, TaskStatus
from backend.orchestrator.sandbox.container_exec import ContainerExecService, ExecutionResponse
from backend.orchestrator.sandbox.snapshot_manager import SnapshotManager

logger = logging.getLogger(__name__)


async def planner_node(session_id: str, issue_description: str) -> TaskGraphState:
    """Planner Agent Node: Initializes the task graph state DAG."""
    logger.info(f"[Planner Node] Generating initial task graph for issue: '{issue_description}'")
    state = TaskPlanner.create_initial_plan(session_id, issue_description)
    return state


async def reproduce_node(node: TaskNode, exec_service: ContainerExecService) -> Dict:
    """Reproduction Agent Node: Executes baseline test suite to confirm issue reproduction."""
    logger.info(f"[Reproduction Node] Executing baseline test run for task '{node.id}'")
    res: ExecutionResponse = await exec_service.execute_command("pytest tests/")
    return {
        "node_id": node.id,
        "reproduction_evidence": res.stdout or res.stderr,
        "exit_code": res.exit_code,
        "reproduced": res.exit_code != 0  # Baseline test failure confirms reproduction
    }


async def coder_node(
    node: TaskNode,
    exec_service: ContainerExecService,
    snapshot_mgr: SnapshotManager,
    edit_command: Optional[str] = None
) -> Dict:
    """Coder Agent Node: Executes sandboxed patch edit and takes checkpoint snapshot."""
    logger.info(f"[Coder Node] Applying code edits for task '{node.id}'")

    # Take pre-edit checkpoint snapshot
    snapshot_mgr.create_checkpoint(step_name=f"pre-{node.id}", description=f"Checkpoint before {node.title}")

    if edit_command:
        res: ExecutionResponse = await exec_service.execute_command(edit_command)
        exit_code = res.exit_code
        stdout = res.stdout
    else:
        # Default code touch check if no specific edit script provided
        res = await exec_service.execute_command("git status")
        exit_code = res.exit_code
        stdout = res.stdout

    # Take post-edit snapshot checkpoint
    post_snap = snapshot_mgr.create_checkpoint(step_name=f"post-{node.id}", description=f"Checkpoint after {node.title}")

    return {
        "node_id": node.id,
        "edit_stdout": stdout,
        "snapshot_id": post_snap.snapshot_id,
        "commit_hash": post_snap.commit_hash,
        "exit_code": exit_code
    }


async def verifier_node(node: TaskNode, exec_service: ContainerExecService) -> Dict:
    """Verifier Agent Node: Runs build, lint, type-check, and test suites inside sandbox."""
    logger.info(f"[Verifier Node] Running verification pipelines for task '{node.id}'")

    # 1. Run Linter
    lint_res = await exec_service.execute_command("ruff check .")

    # 2. Run Type Checker
    type_res = await exec_service.execute_command("mypy .")

    # 3. Run Unit Test Suite
    test_res = await exec_service.execute_command("pytest tests/")

    passed = (test_res.exit_code == 0)

    if not passed:
        raise RuntimeError(f"Verification test suite failed (exit code {test_res.exit_code}). Error: {test_res.stderr or test_res.stdout}")

    return {
        "node_id": node.id,
        "linter_passed": lint_res.exit_code == 0,
        "typecheck_passed": type_res.exit_code == 0,
        "tests_passed": test_res.exit_code == 0,
        "test_summary": test_res.stdout
    }


async def reviewer_node(node: TaskNode, snapshot_mgr: SnapshotManager) -> Dict:
    """Reviewer Agent Node: Compiles final patch diff and completion evidence."""
    logger.info(f"[Reviewer Node] Compiling final completion summary for task '{node.id}'")

    patch_diff = snapshot_mgr.generate_patch()
    snapshots = snapshot_mgr.list_snapshots()

    return {
        "node_id": node.id,
        "patch_diff": patch_diff,
        "total_checkpoints": len(snapshots),
        "latest_snapshot": snapshots[-1].snapshot_id if snapshots else "N/A",
        "verified_complete": True
    }

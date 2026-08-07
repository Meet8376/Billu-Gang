"""Dynamic Replanning Engine for Self-Healing Failure Recovery (Member 4 Lead).

When a verification test, build, or edit fails (FR22), the ReplanningEngine
diagnoses failure outputs and dynamically rewrites/injects new DAG nodes into the Task Graph.
"""

import logging
import uuid
from typing import Optional
from pydantic import BaseModel
from backend.orchestrator.graph.task_planner import TaskGraphState, TaskNode, TaskPlanner, TaskStatus, TaskType

logger = logging.getLogger(__name__)


class DiagnosisResult(BaseModel):
    """Structured diagnosis of a test/build failure."""
    failed_node_id: str
    error_summary: str
    root_cause_hypothesis: str
    recommended_action: str


class ReplanningEngine:
    """Handles dynamic task graph modification and self-healing recovery loops."""

    @staticmethod
    def diagnose_failure(failed_node: TaskNode, error_output: str) -> DiagnosisResult:
        """Analyzes error output to determine failure root cause and recovery steps."""
        error_clean = error_output or failed_node.error_message or "Unknown failure"
        first_line = error_clean.strip().split("\n")[0] if error_clean else "Verification Error"

        return DiagnosisResult(
            failed_node_id=failed_node.id,
            error_summary=first_line[:120],
            root_cause_hypothesis=f"Verification failure in {failed_node.title}: {first_line[:80]}",
            recommended_action="Apply targeted code patch revision addressing failure output and re-verify."
        )

    @staticmethod
    def replan_on_failure(
        state: TaskGraphState,
        failed_node_id: str,
        error_output: str
    ) -> TaskGraphState:
        """Dynamically rewrites remaining DAG nodes when a verification task fails."""
        if failed_node_id not in state.nodes:
            raise KeyError(f"Failed node {failed_node_id} not found in task graph.")

        failed_node = state.nodes[failed_node_id]
        failed_node.status = TaskStatus.FAILED
        failed_node.error_message = error_output

        # Diagnose failure
        diagnosis = ReplanningEngine.diagnose_failure(failed_node, error_output)
        logger.warning(f"[Replanning Engine] Self-healing trigger for '{failed_node.title}'. Diagnosis: {diagnosis.root_cause_hypothesis}")

        # Inject Node A: Replan / Diagnose Node
        diag_node_id = f"diag-{uuid.uuid4().hex[:6]}"
        diag_node = TaskNode(
            id=diag_node_id,
            title=f"Diagnose: {failed_node.title} Failure",
            description=f"Self-healing analysis: {diagnosis.root_cause_hypothesis}",
            task_type=TaskType.REPLAN,
            status=TaskStatus.PENDING,
            dependencies=[failed_node_id]
        )

        # Inject Node B: Revised Patch Node
        fix_node_id = f"fix-{uuid.uuid4().hex[:6]}"
        fix_node = TaskNode(
            id=fix_node_id,
            title=f"Apply Revised Patch (Attempt {failed_node.retry_count + 1})",
            description=f"Apply corrective edits based on diagnosis: {diagnosis.recommended_action}",
            task_type=TaskType.EDIT,
            status=TaskStatus.PENDING,
            dependencies=[diag_node_id]
        )

        # Inject Node C: Re-verify Node
        verify_node_id = f"reverify-{uuid.uuid4().hex[:6]}"
        verify_node = TaskNode(
            id=verify_node_id,
            title=f"Re-Verify Fixed Code",
            description="Re-run build, lint, type-check, and unit test suites.",
            task_type=TaskType.VERIFY,
            status=TaskStatus.PENDING,
            dependencies=[fix_node_id]
        )

        # Add new nodes to graph state
        state.nodes[diag_node_id] = diag_node
        state.nodes[fix_node_id] = fix_node
        state.nodes[verify_node_id] = verify_node

        # Update dependent nodes to point to reverify node
        for n_id, n in state.nodes.items():
            if failed_node_id in n.dependencies and n_id not in (diag_node_id, fix_node_id, verify_node_id):
                n.dependencies.remove(failed_node_id)
                n.dependencies.append(verify_node_id)

        # Set active node pointer to new diagnosis node
        state.active_node_id = diag_node_id
        state.is_failed = False  # Reset failure flag as graph has replanned recovery nodes

        logger.info(f"[Replanning Engine] Injected recovery sub-graph ({diag_node_id} -> {fix_node_id} -> {verify_node_id})")
        return state

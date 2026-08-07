"""
Benchmark Runner Engine (SWE-bench & Terminal-Bench).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import time
import uuid
import tempfile
import shutil
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field

from backend.verification.benchmarking.issue_loader import IssueLoader
from backend.verification.benchmarking.evaluator_grader import EvaluatorGrader, GradeResult


class TaskEvalResult(BaseModel):
    """Result record for a single benchmark task evaluation."""
    issue_id: str = Field(..., description="Benchmark task identifier (e.g. SWE-BENCH-001)")
    benchmark_type: str = Field("swe-bench", description="Benchmark type: swe-bench or terminal-bench")
    success: bool = Field(False, description="True if patch resolves both public and hidden test suites")
    duration_ms: float = Field(0.0, description="Task execution duration in milliseconds")
    cost_usd: float = Field(0.0, description="Financial USD cost attributed to this task run")
    patch_diff: str = Field("", description="Generated patch diff string")
    grade_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed grading output metrics")


class BatchEvalSummary(BaseModel):
    """Summary record for a batch evaluation run across multiple benchmark tasks."""
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique batch evaluation ID")
    benchmark_type: str = Field("swe-bench", description="Benchmark suite type")
    total_tasks: int = Field(0, description="Total number of tasks in batch")
    resolved_tasks: int = Field(0, description="Number of successfully resolved tasks")
    pass_rate: float = Field(0.0, description="Pass rate ratio (0.0 to 1.0)")
    avg_duration_ms: float = Field(0.0, description="Average task duration in milliseconds")
    total_cost_usd: float = Field(0.0, description="Total batch financial USD cost")
    results: List[TaskEvalResult] = Field(default_factory=list, description="Individual task evaluation results")


class BenchmarkRunner:
    """
    Drives batch evaluation across Terminal-Bench and SWE-bench benchmark task sets.
    """

    def __init__(
        self,
        issue_loader: Optional[IssueLoader] = None,
        evaluator_grader: Optional[EvaluatorGrader] = None,
    ):
        self.issue_loader = issue_loader or IssueLoader()
        self.evaluator_grader = evaluator_grader or EvaluatorGrader(issue_loader=self.issue_loader)

    def run_single_task(
        self,
        issue_id: str,
        harness_func: Optional[Callable[[str, str], Tuple[bool, str, float]]] = None,
        workspace_dir: Optional[str] = None,
    ) -> TaskEvalResult:
        """
        Executes evaluation for a single benchmark task.
        `harness_func` receives (workspace_path, problem_statement) and returns (success, patch_diff, cost_usd).
        If harness_func is None, applies ground_truth_patch from issue.
        """
        start_time = time.time()
        issue = self.issue_loader.load_benchmark_issue(issue_id)

        clean_up = False
        if not workspace_dir:
            workspace_dir = tempfile.mkdtemp(prefix=f"bench_{issue_id}_")
            clean_up = True

        try:
            # 1. Setup workspace
            self.issue_loader.setup_issue_workspace(issue_id=issue_id, target_dir=workspace_dir, include_hidden=False)

            patch_diff = ""
            cost_usd = 0.0

            if harness_func:
                _, patch_diff, cost_usd = harness_func(workspace_dir, issue.problem_statement)
            else:
                # Fallback to ground truth patch application stub
                patch_diff = issue.ground_truth_patch
                cost_usd = 0.005

            # 2. Grade submission with hidden test injection
            grade_res: GradeResult = self.evaluator_grader.grade_submission(
                workspace_path=workspace_dir,
                issue_id=issue_id,
                patch=patch_diff,
                hidden_tests=issue.hidden_tests,
            )

            duration_ms = (time.time() - start_time) * 1000.0

            benchmark_type = "terminal-bench" if "TERMINAL" in issue_id else "swe-bench"

            return TaskEvalResult(
                issue_id=issue_id,
                benchmark_type=benchmark_type,
                success=grade_res.resolved,
                duration_ms=duration_ms,
                cost_usd=cost_usd,
                patch_diff=patch_diff,
                grade_details=grade_res.model_dump(mode="json"),
            )
        finally:
            if clean_up and workspace_dir and tempfile.gettempdir() in workspace_dir:
                try:
                    shutil.rmtree(workspace_dir, ignore_errors=True)
                except Exception:
                    pass

    def run_batch(
        self,
        issue_ids: List[str],
        benchmark_type: str = "swe-bench",
        harness_func: Optional[Callable[[str, str], Tuple[bool, str, float]]] = None,
        workspace_root: Optional[str] = None,
    ) -> BatchEvalSummary:
        """
        Executes batch evaluation across multiple task IDs.
        """
        results: List[TaskEvalResult] = []
        resolved_cnt = 0
        total_duration = 0.0
        total_cost = 0.0

        for i_id in issue_ids:
            res = self.run_single_task(
                issue_id=i_id,
                harness_func=harness_func,
                workspace_dir=workspace_root,
            )
            results.append(res)
            if res.success:
                resolved_cnt += 1
            total_duration += res.duration_ms
            total_cost += res.cost_usd

        total = len(issue_ids)
        pass_rate = (resolved_cnt / total) if total > 0 else 0.0
        avg_dur = (total_duration / total) if total > 0 else 0.0

        return BatchEvalSummary(
            benchmark_type=benchmark_type,
            total_tasks=total,
            resolved_tasks=resolved_cnt,
            pass_rate=pass_rate,
            avg_duration_ms=avg_dur,
            total_cost_usd=total_cost,
            results=results,
        )

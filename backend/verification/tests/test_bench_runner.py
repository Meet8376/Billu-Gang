"""
Unit tests for BenchmarkRunner module.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import pytest
from backend.verification.benchmarking.bench_runner import BenchmarkRunner, TaskEvalResult, BatchEvalSummary


def test_benchmark_runner_single_task():
    # Setup runner with mock grader
    runner = BenchmarkRunner()

    def mock_harness(ws_path, prob_stmt):
        return True, "--- diff ---", 0.002

    res: TaskEvalResult = runner.run_single_task(
        issue_id="SWE-BENCH-001",
        harness_func=mock_harness,
    )

    assert res.issue_id == "SWE-BENCH-001"
    assert res.benchmark_type == "swe-bench"
    assert res.cost_usd == 0.002
    assert "grade_details" in res.model_dump()


def test_benchmark_runner_run_batch():
    runner = BenchmarkRunner()

    def mock_harness(ws_path, prob_stmt):
        return True, "--- diff ---", 0.004

    summary: BatchEvalSummary = runner.run_batch(
        issue_ids=["SWE-BENCH-001", "TERMINAL-BENCH-001"],
        benchmark_type="swe-bench",
        harness_func=mock_harness,
    )

    assert summary.total_tasks == 2
    assert len(summary.results) == 2
    assert summary.total_cost_usd == 0.008
    assert summary.avg_duration_ms > 0

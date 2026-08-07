"""
Unit tests for EvaluatorGrader module (FR31).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import pytest
from backend.verification.benchmarking.evaluator_grader import EvaluatorGrader, GradeResult, grade_submission


def test_evaluator_grader_success(tmp_path):
    # Setup mock command executor returning all passed
    def mock_executor(cmd, cwd):
        return 0, "=== 4 passed in 0.15s ===", ""

    grader = EvaluatorGrader(command_executor=mock_executor)
    res: GradeResult = grader.grade_submission(
        workspace_path=str(tmp_path),
        issue_id="SWE-BENCH-001",
        patch="--- sample patch diff ---",
    )

    assert res.issue_id == "SWE-BENCH-001"
    assert res.patch_applied is True
    assert res.resolved is True
    assert res.pass_rate == 1.0
    assert res.details["hidden_tests_injected"] >= 1


def test_evaluator_grader_failure(tmp_path):
    # Setup mock executor returning test failure
    def mock_executor(cmd, cwd):
        return 1, "=== 1 failed, 3 passed in 0.20s ===", ""

    grader = EvaluatorGrader(command_executor=mock_executor)
    res = grader.grade_submission(
        workspace_path=str(tmp_path),
        issue_id="TERMINAL-BENCH-001",
    )

    assert res.resolved is False
    assert res.public_tests_passed is False

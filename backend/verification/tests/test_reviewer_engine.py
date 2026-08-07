"""
Unit tests for ReviewerEngine summary generator.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import pytest
from backend.verification.trace.trace_logger import TraceLogger
from backend.verification.pipeline.runner import VerificationRun, StageResult, VerificationStage
from backend.verification.pipeline.reviewer_engine import ReviewerEngine, ReviewerSummary


def test_reviewer_engine_approved_summary(tmp_path):
    logger = TraceLogger(log_filepath=str(tmp_path / "rev_trace.jsonl"))
    engine = ReviewerEngine(trace_logger=logger)

    v_run = VerificationRun(
        session_id="sess_rev_001",
        success=True,
        duration_ms=450.0,
        stage_results=[
            StageResult(
                stage=VerificationStage.LINT,
                passed=True,
                duration_ms=100.0,
                details={"errors": 0, "warnings": 0},
            ),
            StageResult(
                stage=VerificationStage.TEST,
                passed=True,
                duration_ms=350.0,
                details={"passed": 10, "failed": 0, "total": 10},
            ),
        ],
        summary_message="All verification stages passed.",
    )

    summary: ReviewerSummary = engine.generate_summary(
        session_id="sess_rev_001",
        verification_run=v_run,
        modified_files=["app/main.py", "tests/test_main.py"],
        initial_commit_hash="git_commit_abc123",
        token_cost_usd=0.015,
    )

    assert summary.session_id == "sess_rev_001"
    assert summary.status == "APPROVED"
    assert summary.completeness_proof["tests_passed"] == 10
    assert summary.completeness_proof["lint_errors"] == 0
    assert len(summary.rollback_path["modified_files"]) == 2
    assert summary.cost_info["token_cost_usd"] == 0.015
    assert "# Reviewer Summary" in summary.markdown_report
    assert "APPROVED" in summary.markdown_report


def test_reviewer_engine_rejected_summary():
    engine = ReviewerEngine()

    v_run = VerificationRun(
        session_id="sess_rev_fail",
        success=False,
        stage_results=[
            StageResult(
                stage=VerificationStage.TEST,
                passed=False,
                details={"passed": 2, "failed": 1, "total": 3},
            )
        ],
    )

    summary = engine.generate_summary(
        session_id="sess_rev_fail",
        verification_run=v_run,
    )

    assert summary.status == "REJECTED"
    assert summary.completeness_proof["pipeline_success"] is False
    assert summary.completeness_proof["tests_passed"] == 2


def test_reviewer_engine_needs_revision_due_to_uncertainties():
    engine = ReviewerEngine()

    v_run = VerificationRun(
        session_id="sess_rev_warn",
        success=True,
        stage_results=[
            StageResult(stage=VerificationStage.TEST, passed=True, details={"passed": 5, "total": 5})
        ],
    )

    summary = engine.generate_summary(
        session_id="sess_rev_warn",
        verification_run=v_run,
        uncertainties=["External API endpoint sandbox dependency unverified."],
    )

    assert summary.status == "NEEDS_REVISION"
    assert len(summary.uncertainties) == 1
    assert "External API endpoint" in summary.markdown_report

"""
Unit tests for StaticAnalyzer and VerificationPipeline runner engine.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import pytest
from backend.verification.trace.trace_logger import TraceLogger
from backend.verification.pipeline.static_analyzer import StaticAnalyzer, AnalysisIssue
from backend.verification.pipeline.runner import (
    VerificationPipeline,
    VerificationStage,
    StageResult,
    VerificationRun,
)


def test_static_analyzer_ruff_parser():
    ruff_json = """[
        {
            "code": "F401",
            "message": "`os` imported but unused",
            "location": {"row": 5, "column": 1},
            "filename": "app/main.py"
        }
    ]"""

    issues = StaticAnalyzer.parse_ruff_output(ruff_json)
    assert len(issues) == 1
    assert issues[0].tool == "ruff"
    assert issues[0].code == "F401"
    assert issues[0].file == "app/main.py"
    assert issues[0].line == 5


def test_static_analyzer_mypy_parser():
    mypy_out = """app/main.py:10: error: Incompatible types in assignment (expression has type "str", variable has type "int") [assignment]
app/utils.py:15: note: See https://mypy.readthedocs.io
    """

    issues = StaticAnalyzer.parse_mypy_output(mypy_out)
    assert len(issues) == 1
    assert issues[0].tool == "mypy"
    assert issues[0].file == "app/main.py"
    assert issues[0].line == 10
    assert issues[0].code == "assignment"


def test_static_analyzer_eslint_parser():
    eslint_json = """[
        {
            "filePath": "/src/App.js",
            "messages": [
                {
                    "ruleId": "no-unused-vars",
                    "severity": 2,
                    "message": "'x' is defined but never used.",
                    "line": 12,
                    "column": 5
                }
            ]
        }
    ]"""

    issues = StaticAnalyzer.parse_eslint_output(eslint_json)
    assert len(issues) == 1
    assert issues[0].tool == "eslint"
    assert issues[0].code == "no-unused-vars"
    assert issues[0].severity == "error"


def test_verification_pipeline_run_suite_success(tmp_path):
    log_file = tmp_path / "trace_pipeline_test.jsonl"
    logger = TraceLogger(log_filepath=str(log_file))

    # Mock command executor returning success for all commands
    def mock_executor(cmd, cwd):
        if "ruff" in cmd:
            return 0, "[]", ""
        if "mypy" in cmd:
            return 0, "Success: no issues found in 1 source file", ""
        if "pytest" in cmd:
            return 0, "==== 5 passed in 0.10s ====", ""
        return 0, "Build succeeded", ""

    pipeline = VerificationPipeline(trace_logger=logger, command_executor=mock_executor)
    run_res: VerificationRun = pipeline.run_suite(
        workspace_path=str(tmp_path),
        session_id="sess_verify_001",
        stages=[VerificationStage.LINT, VerificationStage.TYPECHECK, VerificationStage.TEST],
    )

    assert run_res.success is True
    assert len(run_res.stage_results) == 3
    assert all(sr.passed for sr in run_res.stage_results)

    # Check trace events logged
    events = logger.read_traces(session_id="sess_verify_001")
    assert len(events) >= 5  # TEST_RUN_STARTED + 3 VERIFICATION_STEP + TEST_RUN_COMPLETED


def test_verification_pipeline_run_suite_failure(tmp_path):
    log_file = tmp_path / "trace_fail_test.jsonl"
    logger = TraceLogger(log_filepath=str(log_file))

    # Mock executor returning lint error
    def mock_executor(cmd, cwd):
        if "ruff" in cmd:
            return 1, '[{"code": "E999", "message": "SyntaxError", "location": {"row": 1, "column": 1}, "filename": "bad.py"}]', ""
        return 0, "", ""

    pipeline = VerificationPipeline(trace_logger=logger, command_executor=mock_executor)
    run_res = pipeline.run_suite(
        workspace_path=str(tmp_path),
        session_id="sess_verify_fail",
        stages=[VerificationStage.LINT],
    )

    assert run_res.success is False
    assert run_res.stage_results[0].passed is False

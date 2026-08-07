"""
VerificationPipeline Engine.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import time
import uuid
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Tuple
from pydantic import BaseModel, Field

from backend.verification.trace.trace_logger import TraceLogger
from backend.verification.trace.trace_schema import TraceEventType
from backend.verification.pipeline.static_analyzer import StaticAnalyzer, StaticAnalysisResult
from backend.verification.pipeline.test_parsers import (
    parse_pytest_xml,
    parse_pytest_json,
    parse_npm_test,
    TestRunSummary,
)


class VerificationStage(str, Enum):
    """Stages in the Verification Pipeline execution flow."""
    BUILD = "build"
    LINT = "lint"
    TYPECHECK = "typecheck"
    TEST = "test"


class StageResult(BaseModel):
    """Result record of an individual pipeline stage execution."""
    stage: VerificationStage = Field(..., description="Pipeline stage name")
    passed: bool = Field(..., description="Stage success status")
    duration_ms: float = Field(0.0, description="Stage execution time in milliseconds")
    details: Dict[str, Any] = Field(default_factory=dict, description="Structured output/summary dictionary")
    raw_output: str = Field("", description="Raw command output or error message")


class VerificationRun(BaseModel):
    """Complete record of a full verification pipeline execution run."""
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this verification run")
    session_id: str = Field("default", description="Session ID linked to this verification run")
    success: bool = Field(False, description="Overall pipeline success status")
    duration_ms: float = Field(0.0, description="Total pipeline execution duration in milliseconds")
    stage_results: List[StageResult] = Field(default_factory=list, description="Stage execution results")
    summary_message: str = Field("", description="High-level text summary of results")


class VerificationPipeline:
    """
    Verification Pipeline service to trigger build, linting (Ruff/ESLint), type checking (Mypy),
    and test suite execution inside the sandbox workspace as sole proof of completion.
    """

    def __init__(
        self,
        trace_logger: Optional[TraceLogger] = None,
        command_executor: Optional[Callable[[List[str], str], Tuple[int, str, str]]] = None,
    ):
        self.trace_logger = trace_logger or TraceLogger()
        self.command_executor = command_executor
        self.static_analyzer = StaticAnalyzer()

    def _execute_cmd(self, cmd: List[str], cwd: str) -> Tuple[int, str, str]:
        if self.command_executor:
            return self.command_executor(cmd, cwd)
        import subprocess, shutil
        if not shutil.which(cmd[0]):
            return 127, "", f"Executable '{cmd[0]}' not found"
        try:
            res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
            return res.returncode, res.stdout, res.stderr
        except Exception as e:
            return 1, "", str(e)

    def run_build(self, workspace_path: str, command: Optional[List[str]] = None) -> StageResult:
        """Run build verification step (e.g. npm run build or python setup check)."""
        start = time.time()
        cmd = command or ["npm", "run", "build"]
        code, out, err = self._execute_cmd(cmd, workspace_path)
        duration = (time.time() - start) * 1000.0
        passed = (code == 0)

        return StageResult(
            stage=VerificationStage.BUILD,
            passed=passed,
            duration_ms=duration,
            details={"exit_code": code, "cmd": " ".join(cmd)},
            raw_output=out if passed else (err or out),
        )

    def run_lint(self, workspace_path: str, tools: Optional[List[str]] = None) -> StageResult:
        """Run static linter analysis (Ruff / ESLint)."""
        start = time.time()
        lint_tools = tools or ["ruff"]
        analysis_res: StaticAnalysisResult = self.static_analyzer.run_static_analysis(
            target_dir=workspace_path,
            tools=lint_tools,
            executor=self.command_executor,
        )
        duration = (time.time() - start) * 1000.0

        return StageResult(
            stage=VerificationStage.LINT,
            passed=analysis_res.passed,
            duration_ms=duration,
            details=analysis_res.model_dump(mode="json"),
            raw_output=f"Ruff/Linter found {analysis_res.errors} errors, {analysis_res.warnings} warnings.",
        )

    def run_typecheck(self, workspace_path: str) -> StageResult:
        """Run typechecker analysis (Mypy)."""
        start = time.time()
        analysis_res: StaticAnalysisResult = self.static_analyzer.run_static_analysis(
            target_dir=workspace_path,
            tools=["mypy"],
            executor=self.command_executor,
        )
        duration = (time.time() - start) * 1000.0

        return StageResult(
            stage=VerificationStage.TYPECHECK,
            passed=analysis_res.passed,
            duration_ms=duration,
            details=analysis_res.model_dump(mode="json"),
            raw_output=f"Mypy found {analysis_res.errors} type errors.",
        )

    def run_tests(
        self,
        workspace_path: str,
        test_cmd: Optional[List[str]] = None,
        framework: str = "pytest",
    ) -> StageResult:
        """Run test suite runner inside workspace and parse results."""
        start = time.time()
        cmd = test_cmd or ["python", "-m", "pytest", "--junitxml=report.xml"]
        code, out, err = self._execute_cmd(cmd, workspace_path)
        duration = (time.time() - start) * 1000.0

        raw_combined = f"{out}\n{err}".strip()
        summary: TestRunSummary

        if framework == "pytest":
            # Check for xml file report first
            report_file = Path(workspace_path) / "report.xml"
            if report_file.exists():
                summary = parse_pytest_xml(str(report_file))
            elif raw_combined.strip().startswith("<") or "<?xml" in raw_combined:
                summary = parse_pytest_xml(raw_combined)
            else:
                import re
                m_pass = re.search(r"(\d+)\s+passed", raw_combined)
                m_fail = re.search(r"(\d+)\s+failed", raw_combined)
                passed_cnt = int(m_pass.group(1)) if m_pass else 0
                failed_cnt = int(m_fail.group(1)) if m_fail else 0

                if passed_cnt > 0 and failed_cnt == 0:
                    summary = TestRunSummary(
                        framework="pytest_text",
                        passed=passed_cnt,
                        failed=0,
                        total=passed_cnt,
                        raw_output=raw_combined,
                    )
                else:
                    summary = parse_pytest_xml(raw_combined)
        elif framework == "npm":
            summary = parse_npm_test(raw_combined)
        else:
            summary = parse_pytest_xml(raw_combined)

        passed = (code == 0) and summary.is_success

        return StageResult(
            stage=VerificationStage.TEST,
            passed=passed,
            duration_ms=duration,
            details=summary.model_dump(mode="json"),
            raw_output=raw_combined,
        )

    def run_suite(
        self,
        workspace_path: str,
        session_id: str = "default",
        stages: Optional[List[VerificationStage]] = None,
    ) -> VerificationRun:
        """
        Executes configured pipeline stages sequentially, logging events via TraceLogger.
        """
        start_time = time.time()
        if stages is None:
            stages = [VerificationStage.LINT, VerificationStage.TYPECHECK, VerificationStage.TEST]

        self.trace_logger.log_event(
            session_id=session_id,
            event_type=TraceEventType.TEST_RUN_STARTED,
            actor="verification_runner",
            payload={"workspace_path": workspace_path, "stages": [s.value for s in stages]},
        )

        stage_results: List[StageResult] = []
        overall_success = True

        for stage in stages:
            if stage == VerificationStage.BUILD:
                res = self.run_build(workspace_path)
            elif stage == VerificationStage.LINT:
                res = self.run_lint(workspace_path)
            elif stage == VerificationStage.TYPECHECK:
                res = self.run_typecheck(workspace_path)
            elif stage == VerificationStage.TEST:
                res = self.run_tests(workspace_path)
            else:
                continue

            stage_results.append(res)
            self.trace_logger.log_event(
                session_id=session_id,
                event_type=TraceEventType.VERIFICATION_STEP,
                actor="verification_runner",
                payload={"stage": stage.value, "passed": res.passed, "duration_ms": res.duration_ms},
                duration_ms=res.duration_ms,
            )

            if not res.passed:
                overall_success = False

        total_duration = (time.time() - start_time) * 1000.0
        summary_msg = "All verification stages passed." if overall_success else "One or more verification stages failed."

        run_result = VerificationRun(
            session_id=session_id,
            success=overall_success,
            duration_ms=total_duration,
            stage_results=stage_results,
            summary_message=summary_msg,
        )

        self.trace_logger.log_event(
            session_id=session_id,
            event_type=TraceEventType.TEST_RUN_COMPLETED,
            actor="verification_runner",
            payload={"success": overall_success, "stages_run": len(stage_results)},
            duration_ms=total_duration,
        )

        return run_result

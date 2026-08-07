"""
Evaluator Grader & Hidden Test Injection Engine (FR31).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
import shutil
from typing import Dict, Any, Optional, Callable, Tuple
from pydantic import BaseModel, Field

from backend.verification.benchmarking.issue_loader import IssueLoader
from backend.verification.pipeline.test_parsers import parse_pytest_xml, parse_pytest_json, TestRunSummary


class GradeResult(BaseModel):
    """Detailed evaluation grade result for a benchmark submission patch."""
    issue_id: str = Field(..., description="Benchmark issue identifier (e.g. SWE-BENCH-001)")
    patch_applied: bool = Field(True, description="True if submission patch applied cleanly")
    public_tests_passed: bool = Field(False, description="True if public issue unit tests pass")
    hidden_tests_passed: bool = Field(False, description="True if injected hidden evaluation tests pass")
    resolved: bool = Field(False, description="True if submission passes both public and hidden tests (FR31)")
    pass_rate: float = Field(0.0, description="Percentage of overall evaluation tests passed (0.0 - 1.0)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Test summary details for public & hidden runs")
    raw_patch: str = Field("", description="Ground truth or submitted patch diff string")


class EvaluatorGrader:
    """
    Evaluator Grader for hidden test suite injection and ground-truth patch correctness (FR31).
    """

    def __init__(
        self,
        command_executor: Optional[Callable[[list, str], Tuple[int, str, str]]] = None,
        issue_loader: Optional[IssueLoader] = None,
    ):
        self.command_executor = command_executor
        self.issue_loader = issue_loader or IssueLoader()

    def _exec(self, cmd: list, cwd: str) -> Tuple[int, str, str]:
        if self.command_executor:
            return self.command_executor(cmd, cwd)
        import subprocess, shutil as sh
        if not sh.which(cmd[0]):
            return 127, "", f"Executable '{cmd[0]}' not found"
        try:
            res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
            return res.returncode, res.stdout, res.stderr
        except Exception as e:
            return 1, "", str(e)

    def grade_submission(
        self,
        workspace_path: str,
        issue_id: str,
        patch: str = "",
        hidden_tests: Optional[Dict[str, str]] = None,
    ) -> GradeResult:
        """
        Runs evaluation grading against workspace.
        1. Injects hidden test suite into workspace.
        2. Executes test runner.
        3. Evaluates pass rates and cleans up injected hidden tests.
        """
        try:
            issue = self.issue_loader.load_benchmark_issue(issue_id)
            hidden_fixtures = hidden_tests or issue.hidden_tests
        except KeyError:
            hidden_fixtures = hidden_tests or {}

        injected_files: list = []
        try:
            # 1. Inject hidden tests
            for rel_path, content in hidden_fixtures.items():
                full_path = os.path.join(workspace_path, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                injected_files.append(full_path)

            # 2. Run test execution
            code, out, err = self._exec(["python", "-m", "pytest", "--junitxml=report_eval.xml"], workspace_path)
            raw_combined = f"{out}\n{err}".strip()

            eval_xml = os.path.join(workspace_path, "report_eval.xml")
            if os.path.exists(eval_xml):
                summary = parse_pytest_xml(eval_xml)
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

            public_pass = summary.is_success
            hidden_pass = summary.is_success  # If all tests pass including hidden
            total_tests = summary.total
            passed_tests = summary.passed

            pass_rate = (passed_tests / total_tests) if total_tests > 0 else (1.0 if summary.is_success else 0.0)
            resolved = public_pass and hidden_pass and (code == 0)

            return GradeResult(
                issue_id=issue_id,
                patch_applied=True,
                public_tests_passed=public_pass,
                hidden_tests_passed=hidden_pass,
                resolved=resolved,
                pass_rate=pass_rate,
                details={
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": summary.failed,
                    "hidden_tests_injected": len(injected_files),
                },
                raw_patch=patch,
            )
        finally:
            # 3. Clean up injected hidden tests and report file
            for full_path in injected_files:
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception:
                        pass
            eval_xml = os.path.join(workspace_path, "report_eval.xml")
            if os.path.exists(eval_xml):
                try:
                    os.remove(eval_xml)
                except Exception:
                    pass


def grade_submission(
    workspace_path: str,
    issue_id: str,
    patch: str = "",
    hidden_tests: Optional[Dict[str, str]] = None,
) -> GradeResult:
    """Helper module-level function to grade a submission."""
    grader = EvaluatorGrader()
    return grader.grade_submission(workspace_path, issue_id, patch, hidden_tests)

"""
Static Analysis Integration Wrapper (Ruff, ESLint, Mypy).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import json
import subprocess
import shutil
from typing import List, Optional, Dict, Any, Callable, Tuple
from pydantic import BaseModel, Field


class AnalysisIssue(BaseModel):
    """Structured record of a single static analysis finding."""
    tool: str = Field(..., description="Linter or typechecker tool name (ruff, mypy, eslint)")
    file: str = Field(..., description="File path where issue was detected")
    line: Optional[int] = Field(None, description="Line number of issue")
    column: Optional[int] = Field(None, description="Column offset of issue")
    code: Optional[str] = Field(None, description="Diagnostic error/rule code (e.g. F401, no-unused-vars)")
    message: str = Field(..., description="Detailed diagnostic message")
    severity: str = Field("error", description="Severity level: error or warning")


class StaticAnalysisResult(BaseModel):
    """Aggregated static analysis results across linter & typechecker runs."""
    passed: bool = Field(True, description="True if zero error-level issues found")
    total_issues: int = Field(0, description="Total count of issues detected")
    errors: int = Field(0, description="Total count of error-level issues")
    warnings: int = Field(0, description="Total count of warning-level issues")
    issues: List[AnalysisIssue] = Field(default_factory=list, description="List of detected analysis issues")
    tools_run: List[str] = Field(default_factory=list, description="List of tools executed")
    raw_outputs: Dict[str, str] = Field(default_factory=dict, description="Raw stdout/stderr by tool")


class StaticAnalyzer:
    """Static analysis execution wrapper for Ruff, ESLint, and Mypy."""

    @staticmethod
    def parse_ruff_output(output_str: str) -> List[AnalysisIssue]:
        """Parse Ruff JSON or standard text output into AnalysisIssue records."""
        issues: List[AnalysisIssue] = []
        if not output_str.strip():
            return issues

        try:
            items = json.loads(output_str)
            if isinstance(items, list):
                for item in items:
                    fname = item.get("filename", "unknown")
                    code = item.get("code", "")
                    msg = item.get("message", "")
                    location = item.get("location", {})
                    line = location.get("row", None)
                    col = location.get("column", None)
                    issues.append(
                        AnalysisIssue(
                            tool="ruff",
                            file=fname,
                            line=line,
                            column=col,
                            code=code,
                            message=msg,
                            severity="error",
                        )
                    )
                return issues
        except Exception:
            pass

        # Text fallback parsing
        for line in output_str.splitlines():
            line_str = line.strip()
            if not line_str or ":" not in line_str:
                continue
            parts = line_str.split(":", 3)
            if len(parts) >= 3:
                fname = parts[0]
                line_no = int(parts[1]) if parts[1].isdigit() else None
                msg = parts[-1]
                issues.append(
                    AnalysisIssue(
                        tool="ruff",
                        file=fname,
                        line=line_no,
                        message=msg,
                        severity="error",
                    )
                )
        return issues

    @staticmethod
    def parse_mypy_output(output_str: str) -> List[AnalysisIssue]:
        """Parse Mypy output into AnalysisIssue records."""
        issues: List[AnalysisIssue] = []
        for line in output_str.splitlines():
            line_str = line.strip()
            if not line_str or ":" not in line_str or "Success:" in line_str or ": note:" in line_str:
                continue
            parts = line_str.split(":", 3)
            if len(parts) >= 3:
                fname = parts[0]
                line_no = int(parts[1]) if parts[1].isdigit() else None
                status_part = parts[2].strip()
                msg = parts[3].strip() if len(parts) > 3 else status_part

                severity = "error" if "error" in status_part else ("warning" if "note" in status_part or "warning" in status_part else "error")
                
                # Extract code e.g. [attr-defined]
                code = None
                if "[" in msg and msg.endswith("]"):
                    code = msg[msg.rfind("[") + 1 : -1]

                issues.append(
                    AnalysisIssue(
                        tool="mypy",
                        file=fname,
                        line=line_no,
                        code=code,
                        message=msg,
                        severity=severity,
                    )
                )
        return issues

    @staticmethod
    def parse_eslint_output(output_str: str) -> List[AnalysisIssue]:
        """Parse ESLint JSON or text output into AnalysisIssue records."""
        issues: List[AnalysisIssue] = []
        if not output_str.strip():
            return issues

        try:
            files_data = json.loads(output_str)
            if isinstance(files_data, list):
                for f_entry in files_data:
                    filepath = f_entry.get("filePath", "unknown")
                    for msg_entry in f_entry.get("messages", []):
                        severity_num = msg_entry.get("severity", 2)
                        severity = "warning" if severity_num == 1 else "error"
                        issues.append(
                            AnalysisIssue(
                                tool="eslint",
                                file=filepath,
                                line=msg_entry.get("line"),
                                column=msg_entry.get("column"),
                                code=msg_entry.get("ruleId"),
                                message=msg_entry.get("message", ""),
                                severity=severity,
                            )
                        )
                return issues
        except Exception:
            pass

        # Text fallback parsing
        for line in output_str.splitlines():
            line_str = line.strip()
            if "error" in line_str or "warning" in line_str:
                issues.append(
                    AnalysisIssue(
                        tool="eslint",
                        file="unknown",
                        message=line_str,
                        severity="error" if "error" in line_str else "warning",
                    )
                )
        return issues

    def run_static_analysis(
        self,
        target_dir: str,
        tools: Optional[List[str]] = None,
        executor: Optional[Callable[[List[str], str], Tuple[int, str, str]]] = None,
    ) -> StaticAnalysisResult:
        """
        Run static analysis (Ruff, Mypy, ESLint) on target directory.
        `executor` allows running inside a sandbox container if provided.
        """
        if tools is None:
            tools = ["ruff", "mypy"]

        def default_exec(cmd: List[str], cwd: str) -> Tuple[int, str, str]:
            if not shutil.which(cmd[0]):
                return 127, "", f"Command {cmd[0]} not found"
            try:
                proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
                return proc.returncode, proc.stdout, proc.stderr
            except Exception as ex:
                return 1, "", str(ex)

        run_cmd = executor if executor else default_exec

        all_issues: List[AnalysisIssue] = []
        raw_outputs: Dict[str, str] = {}
        executed_tools: List[str] = []

        for tool in tools:
            tool_name = tool.lower()
            executed_tools.append(tool_name)

            if tool_name == "ruff":
                code, out, err = run_cmd(["ruff", "check", "--output-format=json", target_dir], target_dir)
                raw_outputs["ruff"] = out or err
                all_issues.extend(self.parse_ruff_output(out or err))
            elif tool_name == "mypy":
                code, out, err = run_cmd(["mypy", target_dir], target_dir)
                raw_outputs["mypy"] = out or err
                all_issues.extend(self.parse_mypy_output(out or err))
            elif tool_name == "eslint":
                code, out, err = run_cmd(["eslint", "--format=json", target_dir], target_dir)
                raw_outputs["eslint"] = out or err
                all_issues.extend(self.parse_eslint_output(out or err))

        errors = sum(1 for i in all_issues if i.severity == "error")
        warnings = sum(1 for i in all_issues if i.severity == "warning")
        passed = errors == 0

        return StaticAnalysisResult(
            passed=passed,
            total_issues=len(all_issues),
            errors=errors,
            warnings=warnings,
            issues=all_issues,
            tools_run=executed_tools,
            raw_outputs=raw_outputs,
        )

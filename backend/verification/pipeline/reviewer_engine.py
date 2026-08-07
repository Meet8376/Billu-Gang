"""
Reviewer Summary Backend Engine.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.verification.trace.trace_logger import TraceLogger
from backend.verification.pipeline.runner import VerificationRun


class ReviewerSummary(BaseModel):
    """Structured Reviewer Summary output for CLI / UI frontend consumption."""
    session_id: str = Field(..., description="Coding session identifier")
    status: str = Field("APPROVED", description="Overall review decision status: APPROVED, NEEDS_REVISION, REJECTED")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Generation timestamp")
    completeness_proof: Dict[str, Any] = Field(default_factory=dict, description="Proof of done metrics & verification results")
    uncertainties: List[str] = Field(default_factory=list, description="Remaining unverified risk factors or assumptions")
    rollback_path: Dict[str, Any] = Field(default_factory=dict, description="Git snapshot details and rollback instructions")
    cost_info: Dict[str, Any] = Field(default_factory=dict, description="Token consumption and financial cost metrics")
    markdown_report: str = Field("", description="Human-readable markdown summary report")


class ReviewerEngine:
    """
    Reviewer Summary Backend Engine aggregating completeness proof, remaining uncertainties,
    git rollback paths, and token cost attribution.
    """

    def __init__(self, trace_logger: Optional[TraceLogger] = None):
        self.trace_logger = trace_logger or TraceLogger()

    def _render_markdown(
        self,
        session_id: str,
        status: str,
        proof: Dict[str, Any],
        uncertainties: List[str],
        rollback: Dict[str, Any],
        cost: Dict[str, Any],
    ) -> str:
        status_icon = "✅" if status == "APPROVED" else ("⚠️" if status == "NEEDS_REVISION" else "❌")
        lines = [
            f"# Reviewer Summary {status_icon} [{status}]",
            f"**Session ID:** `{session_id}` | **Generated At:** `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`",
            "",
            "## 1. Completeness Proof & Verification Status",
            f"- **Overall Pipeline Success:** `{proof.get('pipeline_success', False)}`",
            f"- **Stages Run:** {proof.get('stages_run_count', 0)}",
            f"- **Total Tests Passed:** {proof.get('tests_passed', 0)} / {proof.get('tests_total', 0)}",
            f"- **Static Analysis Errors:** {proof.get('lint_errors', 0)} (Warnings: {proof.get('lint_warnings', 0)})",
            "",
            "## 2. Remaining Uncertainties & Risk Factors",
        ]

        if uncertainties:
            for u in uncertainties:
                lines.append(f"- ⚠️ {u}")
        else:
            lines.append("- *No unverified risks identified. Proof of completion verified.*")

        lines.extend([
            "",
            "## 3. Rollback Path & Workspace Safety",
            f"- **Initial Git Commit:** `{rollback.get('initial_commit_hash', 'N/A')}`",
            f"- **Modified Files ({len(rollback.get('modified_files', []))}):** " + (", ".join(f"`{f}`" for f in rollback.get("modified_files", [])) or "None"),
            f"- **Rollback Command:** `{rollback.get('rollback_command', 'git reset --hard HEAD')}`",
            "",
            "## 4. Resource & Token Cost Attribution",
            f"- **Estimated USD Cost:** `${cost.get('token_cost_usd', 0.0):.4f}`",
            f"- **Total Duration:** `{cost.get('duration_ms', 0.0):.2f} ms`",
        ])

        return "\n".join(lines)

    def generate_summary(
        self,
        session_id: str,
        verification_run: Optional[VerificationRun] = None,
        modified_files: Optional[List[str]] = None,
        uncertainties: Optional[List[str]] = None,
        initial_commit_hash: Optional[str] = None,
        token_cost_usd: float = 0.0,
    ) -> ReviewerSummary:
        """
        Builds a structured ReviewerSummary object and formatted Markdown report.
        """
        uncertainties_list = uncertainties or []
        mod_files = modified_files or []
        commit_hash = initial_commit_hash or "HEAD~1"

        proof_dict: Dict[str, Any] = {
            "pipeline_success": False,
            "stages_run_count": 0,
            "tests_passed": 0,
            "tests_total": 0,
            "lint_errors": 0,
            "lint_warnings": 0,
        }

        if verification_run:
            proof_dict["pipeline_success"] = verification_run.success
            proof_dict["stages_run_count"] = len(verification_run.stage_results)

            for sr in verification_run.stage_results:
                if sr.stage == "test":
                    dt = sr.details
                    proof_dict["tests_passed"] = dt.get("passed", 0)
                    proof_dict["tests_total"] = dt.get("total", 0)
                elif sr.stage in ("lint", "typecheck"):
                    dt = sr.details
                    proof_dict["lint_errors"] += dt.get("errors", 0)
                    proof_dict["lint_warnings"] += dt.get("warnings", 0)

        # Status logic: APPROVED if pipeline passes and 0 lint errors, NEEDS_REVISION if fails or has uncertainties
        if verification_run and verification_run.success and proof_dict["lint_errors"] == 0:
            status = "NEEDS_REVISION" if uncertainties_list else "APPROVED"
        elif verification_run and not verification_run.success:
            status = "REJECTED"
        else:
            status = "APPROVED" if not uncertainties_list else "NEEDS_REVISION"

        rollback_dict = {
            "initial_commit_hash": commit_hash,
            "modified_files": mod_files,
            "rollback_command": f"git checkout {commit_hash} -- ." if mod_files else "git reset --hard HEAD",
        }

        duration_ms = verification_run.duration_ms if verification_run else 0.0
        cost_dict = {
            "token_cost_usd": token_cost_usd,
            "duration_ms": duration_ms,
        }

        md_report = self._render_markdown(
            session_id=session_id,
            status=status,
            proof=proof_dict,
            uncertainties=uncertainties_list,
            rollback=rollback_dict,
            cost=cost_dict,
        )

        return ReviewerSummary(
            session_id=session_id,
            status=status,
            completeness_proof=proof_dict,
            uncertainties=uncertainties_list,
            rollback_path=rollback_dict,
            cost_info=cost_dict,
            markdown_report=md_report,
        )

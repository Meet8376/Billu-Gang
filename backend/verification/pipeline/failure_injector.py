"""
Synthetic Failure Injector & Snapshot Regression Runner (FR40).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class InjectedFailureScenario(BaseModel):
    """Record of a synthetic failure injected into the workspace for self-healing live demo (FR40)."""
    scenario_id: str = Field(..., description="Unique scenario ID (e.g. DIV_ZERO_BUG, SYNTAX_ERROR)")
    target_file: str = Field(..., description="Relative file path target of failure injection")
    original_snippet: str = Field(..., description="Original working code snippet")
    corrupted_snippet: str = Field(..., description="Corrupted or bug-injected code snippet")
    description: str = Field("", description="Description of injected failure scenario")


class RegressionReport(BaseModel):
    """Report comparing workspace state against an initial git snapshot."""
    has_regressions: bool = Field(False, description="True if unexpected regressions or file deletions detected")
    modified_files: List[str] = Field(default_factory=list, description="Files modified compared to snapshot")
    added_files: List[str] = Field(default_factory=list, description="New files added compared to snapshot")
    deleted_files: List[str] = Field(default_factory=list, description="Files deleted compared to snapshot")
    diff_summary: str = Field("", description="Human-readable summary of snapshot differences")


class FailureInjector:
    """
    Synthetic Failure Injector for live demonstration of injected failure self-healing flows (FR40).
    """

    DEFAULT_SCENARIOS = {
        "DIV_ZERO_BUG": InjectedFailureScenario(
            scenario_id="DIV_ZERO_BUG",
            target_file="calculator.py",
            original_snippet="return a / b",
            corrupted_snippet="return b / a  # INJECTED BUG",
            description="Reverses division parameters to cause unit test assertion failures.",
        ),
        "SYNTAX_ERROR": InjectedFailureScenario(
            scenario_id="SYNTAX_ERROR",
            target_file="calculator.py",
            original_snippet="def add(a: float, b: float) -> float:",
            corrupted_snippet="def add(a: float, b: float) -> float  # INJECTED SYNTAX ERROR",
            description="Removes trailing colon to cause syntax check failures.",
        ),
    }

    def inject_synthetic_failure(
        self,
        workspace_path: str,
        scenario_id: str = "DIV_ZERO_BUG",
        custom_scenario: Optional[InjectedFailureScenario] = None,
    ) -> InjectedFailureScenario:
        """
        Injects a synthetic bug/failure scenario into the target workspace.
        """
        scenario = custom_scenario or self.DEFAULT_SCENARIOS.get(scenario_id)
        if not scenario:
            raise KeyError(f"Failure scenario '{scenario_id}' not found.")

        target_filepath = os.path.join(workspace_path, scenario.target_file)
        if not os.path.exists(target_filepath):
            # Create stub target file if missing
            with open(target_filepath, "w", encoding="utf-8") as f:
                f.write(scenario.original_snippet + "\n")

        with open(target_filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if scenario.original_snippet in content:
            new_content = content.replace(scenario.original_snippet, scenario.corrupted_snippet)
        else:
            new_content = content + "\n" + scenario.corrupted_snippet

        with open(target_filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        return scenario

    def restore_injected_failure(
        self,
        workspace_path: str,
        scenario: InjectedFailureScenario,
    ) -> bool:
        """
        Restores workspace file back to original snippet prior to failure injection.
        """
        target_filepath = os.path.join(workspace_path, scenario.target_file)
        if not os.path.exists(target_filepath):
            return False

        with open(target_filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if scenario.corrupted_snippet in content:
            new_content = content.replace(scenario.corrupted_snippet, scenario.original_snippet)
            with open(target_filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        return False


class RegressionRunner:
    """
    Regression Test Runner comparing workspace files against initial git snapshot dictionary.
    """

    def check_regression_against_snapshot(
        self,
        workspace_path: str,
        initial_snapshot_files: Dict[str, str],
    ) -> RegressionReport:
        """
        Compares current files in workspace with initial snapshot.
        """
        modified: List[str] = []
        added: List[str] = []
        deleted: List[str] = []

        # Check existing snapshot files
        for rel_path, orig_content in initial_snapshot_files.items():
            full_path = os.path.join(workspace_path, rel_path)
            if not os.path.exists(full_path):
                deleted.append(rel_path)
            else:
                with open(full_path, "r", encoding="utf-8") as f:
                    curr_content = f.read()
                if curr_content != orig_content:
                    modified.append(rel_path)

        # Check for newly added files
        for root, _, files in os.walk(workspace_path):
            for file in files:
                if file.startswith(".") or file.endswith(".pyc"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, workspace_path).replace("\\", "/")
                if rel_path not in initial_snapshot_files:
                    added.append(rel_path)

        has_regressions = len(deleted) > 0 or len(modified) > 0
        diff_summary = f"Modified: {len(modified)}, Added: {len(added)}, Deleted: {len(deleted)}"

        return RegressionReport(
            has_regressions=has_regressions,
            modified_files=modified,
            added_files=added,
            deleted_files=deleted,
            diff_summary=diff_summary,
        )

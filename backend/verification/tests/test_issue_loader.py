"""
Unit tests for IssueLoader module.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
import pytest
from backend.verification.benchmarking.issue_loader import IssueLoader, load_benchmark_issue


def test_issue_loader_default_issues():
    loader = IssueLoader()
    issues = loader.list_available_issues()
    assert len(issues) >= 2

    issue_ids = [i["issue_id"] for i in issues]
    assert "SWE-BENCH-001" in issue_ids
    assert "TERMINAL-BENCH-001" in issue_ids


def test_load_benchmark_issue_success():
    issue = load_benchmark_issue("SWE-BENCH-001")
    assert issue.issue_id == "SWE-BENCH-001"
    assert "TextProcessor" in issue.problem_statement
    assert "text_processor.py" in issue.repo_files


def test_load_benchmark_issue_invalid():
    loader = IssueLoader()
    with pytest.raises(KeyError):
        loader.load_benchmark_issue("NONEXISTENT-ISSUE-999")


def test_setup_issue_workspace(tmp_path):
    loader = IssueLoader()
    target_dir = tmp_path / "workspace_test"

    out_dir = loader.setup_issue_workspace(
        issue_id="TERMINAL-BENCH-001",
        target_dir=str(target_dir),
        include_hidden=True,
    )

    assert os.path.exists(os.path.join(out_dir, "cli_parser.py"))
    assert os.path.exists(os.path.join(out_dir, "test_cli_parser.py"))
    assert os.path.exists(os.path.join(out_dir, "test_hidden_quotes.py"))

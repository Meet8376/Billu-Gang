"""
Phase 1 Unit Tests for Sample Target Repositories & Benchmark Test Issues.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
from backend.verification.benchmarking.sample_repos import (
    get_sample_bug_repo,
    get_sample_benchmark_issue,
    setup_sample_repo_in_dir,
)


def test_sample_bug_repo_fixture():
    bug_repo = get_sample_bug_repo()
    assert bug_repo.name == "sample-calculator-bug"
    assert "calculator.py" in bug_repo.files
    assert "test_calculator.py" in bug_repo.files
    assert "test_calculator.py::test_divide" in bug_repo.expected_failing_test


def test_benchmark_test_issue_fixture():
    issue = get_sample_benchmark_issue()
    assert issue.issue_id == "SWE-BENCH-001"
    assert "text_processor.py" in issue.repo_files
    assert "test_hidden_eval.py" in issue.hidden_tests
    assert issue.test_command == "pytest"


def test_setup_sample_repo_in_dir(tmp_path):
    target_dir = str(tmp_path / "test_repo_workspace")
    setup_sample_repo_in_dir(target_dir=target_dir, repo_type="bug")

    calc_file = os.path.join(target_dir, "calculator.py")
    test_file = os.path.join(target_dir, "test_calculator.py")
    assert os.path.exists(calc_file)
    assert os.path.exists(test_file)

    with open(calc_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "def divide(a: float, b: float)" in content


def test_setup_benchmark_repo_in_dir(tmp_path):
    target_dir = str(tmp_path / "benchmark_workspace")
    setup_sample_repo_in_dir(target_dir=target_dir, repo_type="benchmark")

    proc_file = os.path.join(target_dir, "text_processor.py")
    assert os.path.exists(proc_file)

    with open(proc_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "class TextProcessor" in content

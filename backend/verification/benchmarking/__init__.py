"""
Benchmarking & Evaluation Package.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

from backend.verification.benchmarking.sample_repos import (
    SampleBugRepo,
    BenchmarkTestIssue,
    get_sample_bug_repo,
    get_sample_benchmark_issue,
    setup_sample_repo_in_dir,
)
from backend.verification.benchmarking.issue_loader import (
    IssueLoader,
    load_benchmark_issue,
)
from backend.verification.benchmarking.evaluator_grader import (
    EvaluatorGrader,
    GradeResult,
    grade_submission,
)

__all__ = [
    "SampleBugRepo",
    "BenchmarkTestIssue",
    "get_sample_bug_repo",
    "get_sample_benchmark_issue",
    "setup_sample_repo_in_dir",
    "IssueLoader",
    "load_benchmark_issue",
    "EvaluatorGrader",
    "GradeResult",
    "grade_submission",
]

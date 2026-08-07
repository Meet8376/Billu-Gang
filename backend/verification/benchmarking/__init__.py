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
from backend.verification.benchmarking.bench_runner import (
    BenchmarkRunner,
    TaskEvalResult,
    BatchEvalSummary,
)
from backend.verification.benchmarking.ablation_protocol import (
    AblationProtocolEngine,
    AblationVariantResult,
    AblationMatrixReport,
)
from backend.verification.benchmarking.demo_script import (
    VerificationDemo,
    run_pitch_demonstration,
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
    "BenchmarkRunner",
    "TaskEvalResult",
    "BatchEvalSummary",
    "AblationProtocolEngine",
    "AblationVariantResult",
    "AblationMatrixReport",
    "VerificationDemo",
    "run_pitch_demonstration",
]

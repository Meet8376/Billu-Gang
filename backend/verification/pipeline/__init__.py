"""
Verification Pipeline & Quality Check Package.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

from backend.verification.pipeline.test_parsers import (
    TestResultStatus,
    TestCaseResult,
    TestRunSummary,
    parse_pytest_xml,
    parse_pytest_json,
    parse_npm_test,
)
from backend.verification.pipeline.static_analyzer import (
    AnalysisIssue,
    StaticAnalysisResult,
    StaticAnalyzer,
)
from backend.verification.pipeline.runner import (
    VerificationStage,
    StageResult,
    VerificationRun,
    VerificationPipeline,
)
from backend.verification.pipeline.reviewer_engine import (
    ReviewerSummary,
    ReviewerEngine,
)
from backend.verification.pipeline.failure_injector import (
    InjectedFailureScenario,
    RegressionReport,
    FailureInjector,
    RegressionRunner,
)

__all__ = [
    "TestResultStatus",
    "TestCaseResult",
    "TestRunSummary",
    "parse_pytest_xml",
    "parse_pytest_json",
    "parse_npm_test",
    "AnalysisIssue",
    "StaticAnalysisResult",
    "StaticAnalyzer",
    "VerificationStage",
    "StageResult",
    "VerificationRun",
    "VerificationPipeline",
    "ReviewerSummary",
    "ReviewerEngine",
    "InjectedFailureScenario",
    "RegressionReport",
    "FailureInjector",
    "RegressionRunner",
]

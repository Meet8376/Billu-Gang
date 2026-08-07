"""
Unit tests for AblationProtocolEngine module (FR47).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import pytest
from backend.verification.benchmarking.ablation_protocol import (
    AblationProtocolEngine,
    AblationMatrixReport,
)


def test_ablation_protocol_run_matrix():
    engine = AblationProtocolEngine()

    report: AblationMatrixReport = engine.run_ablation_matrix(
        matrix_name="tiered_memory_toggle",
        issue_ids=["SWE-BENCH-001"],
    )

    assert "Matrix 2" in report.matrix_name
    assert "memory_on" in report.variants
    assert "memory_off" in report.variants
    assert report.winner_variant in ("memory_on", "memory_off")
    assert "| `memory_on` |" in report.markdown_summary


def test_ablation_protocol_run_full_study():
    engine = AblationProtocolEngine()

    full_study = engine.run_full_ablation_study(issue_ids=["SWE-BENCH-001", "TERMINAL-BENCH-001"])

    assert len(full_study) == 3
    assert "baseline_vs_submitted" in full_study
    assert "tiered_memory_toggle" in full_study
    assert "topology_comparison" in full_study

    md_report = engine.generate_ablation_report_markdown(full_study)
    assert "# Standardized Ablation & Performance Report (FR47)" in md_report
    assert "Matrix 1" in md_report
    assert "Matrix 2" in md_report
    assert "Matrix 3" in md_report

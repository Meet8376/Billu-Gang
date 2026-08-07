"""
Phase 6 Final Integration Verification Test Suite.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import pytest
from backend.verification.benchmarking.demo_script import run_pitch_demonstration, VerificationDemo


def test_phase6_pitch_demonstration_execution():
    evidence = run_pitch_demonstration()

    assert evidence["demo_status"] == "SUCCESS"
    assert evidence["injected_failure_detected"] is True
    assert evidence["self_healing_restored"] is True
    assert evidence["trace_events_logged"] > 0
    assert evidence["reviewer_status"] in ("APPROVED", "NEEDS_REVISION")
    assert evidence["ablation_matrices_evaluated"] == 3
    assert "# Standardized Ablation & Performance Report" in evidence["ablation_report_markdown"]


def test_phase6_verification_demo_instance():
    demo = VerificationDemo()
    evidence = demo.run_demo()

    assert evidence["demo_status"] == "SUCCESS"
    assert "Matrix 1" in evidence["ablation_report_markdown"]
    assert "Matrix 2" in evidence["ablation_report_markdown"]
    assert "Matrix 3" in evidence["ablation_report_markdown"]

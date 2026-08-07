"""
Unit tests for FailureInjector and RegressionRunner modules (FR40).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
import pytest
from backend.verification.pipeline.failure_injector import (
    FailureInjector,
    RegressionRunner,
    InjectedFailureScenario,
)


def test_failure_injector_injection_and_restore(tmp_path):
    injector = FailureInjector()

    calc_file = tmp_path / "calculator.py"
    calc_file.write_text("def divide(a, b):\n    return a / b\n", encoding="utf-8")

    scenario = injector.inject_synthetic_failure(
        workspace_path=str(tmp_path),
        scenario_id="DIV_ZERO_BUG",
    )

    assert scenario.scenario_id == "DIV_ZERO_BUG"
    content_after = calc_file.read_text(encoding="utf-8")
    assert "return b / a" in content_after

    # Restore
    restored = injector.restore_injected_failure(
        workspace_path=str(tmp_path),
        scenario=scenario,
    )
    assert restored is True
    content_restored = calc_file.read_text(encoding="utf-8")
    assert "return a / b" in content_restored


def test_regression_runner_snapshot_check(tmp_path):
    runner = RegressionRunner()

    # Initial snapshot dict
    snapshot = {
        "file1.py": "print('hello')",
        "file2.py": "x = 10",
    }

    # Setup workspace matching snapshot
    f1 = tmp_path / "file1.py"
    f2 = tmp_path / "file2.py"
    f1.write_text("print('hello')", encoding="utf-8")
    f2.write_text("x = 10", encoding="utf-8")

    # Initial check (no regressions)
    rep1 = runner.check_regression_against_snapshot(str(tmp_path), snapshot)
    assert rep1.has_regressions is False
    assert len(rep1.modified_files) == 0

    # Modify file1 and delete file2
    f1.write_text("print('modified')", encoding="utf-8")
    os.remove(str(f2))

    rep2 = runner.check_regression_against_snapshot(str(tmp_path), snapshot)
    assert rep2.has_regressions is True
    assert "file1.py" in rep2.modified_files
    assert "file2.py" in rep2.deleted_files

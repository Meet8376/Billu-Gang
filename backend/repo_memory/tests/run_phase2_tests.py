"""
Phase 2 Test Runner Script

Runs all Phase 2 tests in backend/repo_memory/tests/ using pytest programmatically
and outputs formatted test results.
"""

import sys
import os
from pathlib import Path

# Add repository root to sys.path so backend package is resolved
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

import pytest


def run_tests():
    print("=" * 70)
    print("AE-01 Repo Intelligence & Tiered Memory - Phase 2 Test Suite")
    print("=" * 70)
    
    tests_dir = Path(__file__).resolve().parent
    print(f"📁 Running tests in: {tests_dir}\n")
    
    # Run pytest programmatically
    args = [
        str(tests_dir),
        "-v",
        "--tb=short",
    ]
    
    exit_code = pytest.main(args)
    
    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ ALL PHASE 2 TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"❌ TEST SUITE COMPLETED WITH EXIT CODE {exit_code}")
    print("=" * 70)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())

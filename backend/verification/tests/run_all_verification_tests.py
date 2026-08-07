"""
Verification Test Runner Script for Member 5 Test Suite.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import sys
import pytest
from pathlib import Path

def main():
    test_dir = str(Path(__file__).parent)
    print(f"=== Running Member 5 Verification Test Suite in {test_dir} ===")
    
    # Run pytest programmatically
    args = [
        "-v",
        "--tb=short",
        test_dir
    ]
    
    exit_code = pytest.main(args)
    print(f"\n=== Test Run Completed with Exit Code: {exit_code} ===")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

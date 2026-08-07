"""
Test Target Repositories & Benchmark Test Issue Fixtures (Phase 1).
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class SampleBugRepo:
    """Sample repository containing a known bug for verification & healing test suites."""

    name: str = "sample-calculator-bug"
    description: str = "Python calculation module with division bug and unit tests."
    files: Dict[str, str] = field(
        default_factory=lambda: {
            "calculator.py": '''"""Calculator Module."""

def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    return a * b

def divide(a: float, b: float) -> float:
    # BUG: Returns b / a instead of a / b
    return b / a
''',
            "test_calculator.py": '''"""Calculator Unit Tests."""
import pytest
from calculator import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 2) == 3

def test_multiply():
    assert multiply(3, 4) == 12

def test_divide():
    assert divide(10, 2) == 5  # Fails due to bug returning 2 / 10 = 0.2
''',
            "pytest.ini": "[pytest]\npython_files = test_*.py\n",
        }
    )
    expected_failing_test: str = "test_calculator.py::test_divide"
    expected_patch: str = """--- calculator.py
+++ calculator.py
@@ -12,2 +12,2 @@
 def divide(a: float, b: float) -> float:
-    return b / a
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
+    return a / b
"""


@dataclass
class BenchmarkTestIssue:
    """Benchmark problem issue representation (SWE-bench / Terminal-Bench style)."""

    issue_id: str = "SWE-BENCH-001"
    title: str = "TextProcessor fails to normalize multiline markdown headers"
    problem_statement: str = (
        "The TextProcessor module does not strip whitespace when parsing header "
        "titles in markdown strings. Fix `format_header` to strip leading/trailing whitespace."
    )
    repo_files: Dict[str, str] = field(
        default_factory=lambda: {
            "text_processor.py": '''"""Text Processor Module."""

class TextProcessor:
    def format_header(self, raw_header: str) -> str:
        # BUG: Missing .strip() on header content
        return f"# {raw_header}"
''',
            "test_text_processor.py": '''"""Text Processor Public Tests."""
from text_processor import TextProcessor

def test_format_header_basic():
    tp = TextProcessor()
    assert tp.format_header("Title") == "# Title"
''',
        }
    )
    hidden_tests: Dict[str, str] = field(
        default_factory=lambda: {
            "test_hidden_eval.py": '''"""Hidden Evaluation Test Suite for SWE-bench Grader."""
from text_processor import TextProcessor

def test_format_header_whitespace_hidden():
    tp = TextProcessor()
    assert tp.format_header("   Padded Title   ") == "# Padded Title"
'''
        }
    )
    test_command: str = "pytest"
    ground_truth_patch: str = """--- text_processor.py
+++ text_processor.py
@@ -4,3 +4,3 @@
     def format_header(self, raw_header: str) -> str:
-        return f"# {raw_header}"
+        return f"# {raw_header.strip()}"
"""


def get_sample_bug_repo() -> SampleBugRepo:
    """Return instance of SampleBugRepo."""
    return SampleBugRepo()


def get_sample_benchmark_issue() -> BenchmarkTestIssue:
    """Return instance of BenchmarkTestIssue."""
    return BenchmarkTestIssue()


def setup_sample_repo_in_dir(target_dir: str, repo_type: str = "bug") -> str:
    """Write sample repo files into target_dir on disk."""
    os.makedirs(target_dir, exist_ok=True)
    if repo_type == "benchmark":
        issue = get_sample_benchmark_issue()
        for filename, content in issue.repo_files.items():
            filepath = os.path.join(target_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
    else:
        bug_repo = get_sample_bug_repo()
        for filename, content in bug_repo.files.items():
            filepath = os.path.join(target_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
    return target_dir

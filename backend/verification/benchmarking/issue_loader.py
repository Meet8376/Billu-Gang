"""
Benchmark Problem Loader & Workspace Feeder.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
from typing import Dict, List, Any, Optional
from backend.verification.benchmarking.sample_repos import BenchmarkTestIssue, get_sample_benchmark_issue, get_sample_bug_repo


class IssueLoader:
    """
    Benchmark loader for SWE-bench & Terminal-Bench task instances.
    Feeds problem statements, sets up target workspace, and provides hidden test injection.
    """

    def __init__(self, custom_issues: Optional[Dict[str, BenchmarkTestIssue]] = None):
        self._registry: Dict[str, BenchmarkTestIssue] = {}
        
        # Load default benchmark issue fixtures
        def_issue = get_sample_benchmark_issue()
        self._registry[def_issue.issue_id] = def_issue

        # Terminal-Bench sample issue fixture
        terminal_issue = BenchmarkTestIssue(
            issue_id="TERMINAL-BENCH-001",
            title="CLI argument parsing fails on nested flags",
            problem_statement="The CLI tool crashes when parsing double-dash flags inside quotes. Update parser to ignore quoted dashes.",
            repo_files={
                "cli_parser.py": 'def parse_args(raw: str):\n    # BUG: naive split\n    return raw.split()\n',
                "test_cli_parser.py": 'from cli_parser import parse_args\ndef test_basic():\n    assert len(parse_args("a b")) == 2\n',
            },
            hidden_tests={
                "test_hidden_quotes.py": 'from cli_parser import parse_args\ndef test_quoted():\n    assert parse_args(\'a "--flag value"\') == ["a", "--flag value"]\n',
            },
            ground_truth_patch="--- cli_parser.py\n+++ cli_parser.py\n@@ -1,2 +1,3 @@\n+import shlex\n def parse_args(raw: str):\n-    return raw.split()\n+    return shlex.split(raw)\n",
        )
        self._registry[terminal_issue.issue_id] = terminal_issue

        if custom_issues:
            self._registry.update(custom_issues)

    def load_benchmark_issue(self, issue_id: str) -> BenchmarkTestIssue:
        """Loads and returns a BenchmarkTestIssue by issue_id."""
        if issue_id not in self._registry:
            raise KeyError(f"Benchmark issue '{issue_id}' not found in issue registry. Available: {list(self._registry.keys())}")
        return self._registry[issue_id]

    def list_available_issues(self) -> List[Dict[str, str]]:
        """Returns metadata list of all available benchmark problem issues."""
        results = []
        for issue_id, issue in self._registry.items():
            results.append({
                "issue_id": issue_id,
                "title": issue.title,
                "problem_statement": issue.problem_statement[:120] + ("..." if len(issue.problem_statement) > 120 else ""),
                "repo_files_count": len(issue.repo_files),
                "hidden_tests_count": len(issue.hidden_tests),
            })
        return results

    def setup_issue_workspace(
        self,
        issue_id: str,
        target_dir: str,
        include_hidden: bool = False,
    ) -> str:
        """
        Initializes target directory on disk with repository files from the specified issue.
        Optionally writes hidden evaluation tests if include_hidden is True.
        """
        issue = self.load_benchmark_issue(issue_id)
        os.makedirs(target_dir, exist_ok=True)

        for rel_path, content in issue.repo_files.items():
            full_path = os.path.join(target_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        if include_hidden:
            for rel_path, content in issue.hidden_tests.items():
                full_path = os.path.join(target_dir, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

        return target_dir


def load_benchmark_issue(issue_id: str) -> BenchmarkTestIssue:
    """Helper module-level function to load benchmark issue by ID."""
    loader = IssueLoader()
    return loader.load_benchmark_issue(issue_id)

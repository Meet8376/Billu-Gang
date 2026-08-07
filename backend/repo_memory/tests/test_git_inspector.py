"""
Unit tests for GitInspector (indexer/git_inspector.py)
"""

import pytest
import os
import tempfile

from backend.repo_memory.indexer.git_inspector import GitInspector, GitInspectorError


def test_git_inspector_non_git_repo():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Non-git repository directory should raise GitInspectorError
        with pytest.raises(GitInspectorError):
            GitInspector(tmp_dir)


def test_git_inspector_with_current_repo():
    repo_path = os.getcwd()
    try:
        inspector = GitInspector(repo_path)
        info = inspector.get_repo_info()
        assert "current_branch" in info or "error" in info
    except GitInspectorError:
        pytest.skip("Git repo context not available")

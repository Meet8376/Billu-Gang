"""
Unit tests for TestMapper (indexer/test_mapper.py)
"""

import pytest
import os
import tempfile
from pathlib import Path

from backend.repo_memory.indexer.test_mapper import TestMapper


@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create source files and test files
        src_dir = Path(tmp_dir) / "src"
        test_dir = Path(tmp_dir) / "tests"
        src_dir.mkdir(parents=True)
        test_dir.mkdir(parents=True)

        (src_dir / "auth.py").write_text("def login(): pass\n")
        (src_dir / "user.py").write_text("class User: pass\n")
        
        (test_dir / "test_auth.py").write_text("from src.auth import login\ndef test_login(): pass\n")
        (test_dir / "test_user.py").write_text("from src.user import User\ndef test_user(): pass\n")

        yield tmp_dir


def test_test_mapper_indexing(temp_repo):
    mapper = TestMapper(temp_repo)
    stats = mapper.get_stats()
    assert stats["test_files"] >= 2
    assert stats["source_files"] >= 2


def test_find_related_tests(temp_repo):
    mapper = TestMapper(temp_repo)
    results = mapper.find_related_tests("src/auth.py")
    assert len(results) >= 1
    test_path, confidence = results[0]
    assert "test_auth.py" in test_path
    assert confidence > 0.5


def test_find_source_for_test(temp_repo):
    mapper = TestMapper(temp_repo)
    results = mapper.find_source_for_test("tests/test_user.py")
    assert len(results) >= 1
    source_path, confidence = results[0]
    assert "user.py" in source_path
    assert confidence > 0.5

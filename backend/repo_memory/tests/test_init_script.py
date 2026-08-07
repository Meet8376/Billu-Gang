"""
Unit tests for initialize_harness_repo_memory (db/init_script.py)
"""

import pytest
import os
from tempfile import TemporaryDirectory
from pathlib import Path

from backend.repo_memory.db.init_script import initialize_harness_repo_memory


def test_initialize_harness_repo_memory():
    with TemporaryDirectory() as repo_dir:
        # Add sample file
        sample_file = Path(repo_dir) / "main.py"
        sample_file.write_text("print('hello world')")

        db_path = os.path.join(repo_dir, "harness.db")
        result = initialize_harness_repo_memory(
            repo_path=repo_dir,
            db_path=db_path,
            model_provider="anthropic"
        )

        assert result["status"] == "initialized"
        assert result["scanned_files_count"] >= 1
        assert os.path.exists(db_path)

"""
Unit tests for FileSummarizer (context/summarizer.py)
"""

import pytest
from tempfile import NamedTemporaryFile
import os

from backend.repo_memory.context.summarizer import FileSummarizer, summarize_file


@pytest.fixture
def temp_python_file():
    code = """
import os

class UserAuthService:
    def __init__(self, db):
        self.db = db

    def login(self, username, password):
        return True

def standalone_helper():
    pass
"""
    with NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
        tmp.write(code)
        path = tmp.name

    yield path

    if os.path.exists(path):
        os.remove(path)


def test_file_summarizer(temp_python_file):
    summarizer = FileSummarizer()
    summary = summarizer.summarize(temp_python_file)
    
    assert "File Outline:" in summary
    assert "UserAuthService" in summary or "standalone_helper" in summary


def test_summarize_file_convenience(temp_python_file):
    summary = summarize_file(temp_python_file)
    assert len(summary) > 0
    assert "File Outline:" in summary

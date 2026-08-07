"""
Unit tests for IncrementalIndexer (indexer/incremental_indexer.py)
"""

import pytest
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path

from backend.repo_memory.db.database import init_db, close_db, get_db_session
from backend.repo_memory.db.models import SessionModel, SymbolIndexModel
from backend.repo_memory.indexer.incremental_indexer import IncrementalIndexer


@pytest.fixture
def temp_environment():
    with NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name
    init_db(db_path, force_recreate=True)

    with TemporaryDirectory() as repo_dir:
        # Create session
        with get_db_session(db_path) as session:
            repo_session = SessionModel(repo_path=repo_dir, model_provider="test")
            session.add(repo_session)
            session.commit()
            session_id = repo_session.id

        yield db_path, session_id, repo_dir

    close_db()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        pass



def test_incremental_indexer_refresh(temp_environment):
    db_path, session_id, repo_dir = temp_environment

    # Create a Python file in repo_dir
    file_path = Path(repo_dir) / "auth.py"
    file_path.write_text("""
def login_user(username, password):
    return True

class SessionToken:
    def validate(self):
        return True
""")

    indexer = IncrementalIndexer(session_id, repo_dir, db_path)
    stats = indexer.refresh_files(["auth.py"])

    assert stats["files_processed"] == 1
    assert stats["symbols_updated"] >= 2

    # Verify symbol index in database
    with get_db_session(db_path) as session:
        symbols = session.query(SymbolIndexModel).filter_by(session_id=session_id).all()
        assert len(symbols) >= 2
        names = {s.symbol_name for s in symbols}
        assert "login_user" in names
        assert "SessionToken" in names

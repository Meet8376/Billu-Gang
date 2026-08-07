"""
Unit tests for ContextManager (context/context_manager.py)
"""

import pytest
import os
from tempfile import NamedTemporaryFile

from backend.repo_memory.db.database import init_db, close_db, get_db_session
from backend.repo_memory.db.models import SessionModel, MemoryTier
from backend.repo_memory.memory.tiered_store import TieredMemoryStore
from backend.repo_memory.context.context_manager import ContextManager


@pytest.fixture
def temp_db():
    with NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    init_db(db_path, force_recreate=True)

    with get_db_session(db_path) as session:
        repo_session = SessionModel(repo_path="/fake/repo", model_provider="test")
        session.add(repo_session)
        session.commit()
        session_id = repo_session.id

    yield db_path, session_id

    close_db()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        pass


def test_context_manager_assembly(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)

    # Seed memories
    store.add(tier=MemoryTier.PROJECT, content="Always use PostgreSQL database pool")
    store.add(tier=MemoryTier.TASK, content="Implement user login token endpoint")

    cm = ContextManager(session_id, db_path, default_max_tokens=2000)

    result = cm.assemble_context(
        query="Help me build login endpoint with sk-1234567890abcdef1234567890abcdef12",
        system_instructions="You are an expert backend engineer."
    )

    assert "prompt" in result
    assert result["token_count"] > 0
    assert len(result["included_memories"]) >= 1
    # Check that secrets in query were sanitized
    assert "sk-1234" not in result["sanitized_query"]
    assert "[REDACTED_OPENAI_KEY]" in result["sanitized_query"] or "[REDACTED_OPENAI_API_KEY]" in result["sanitized_query"]


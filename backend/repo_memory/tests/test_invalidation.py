"""
Unit tests for MemoryInvalidator (memory/invalidation.py)
"""

import pytest
import os
from tempfile import NamedTemporaryFile

from backend.repo_memory.db.database import init_db, get_db_session
from backend.repo_memory.db.models import SessionModel, MemoryTier
from backend.repo_memory.memory.tiered_store import TieredMemoryStore
from backend.repo_memory.memory.invalidation import MemoryInvalidator, invalidate_stale_memories


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

    if os.path.exists(db_path):
        os.remove(db_path)


def test_invalidation_by_source_file(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    
    item1 = store.add(tier=MemoryTier.WORKING, content="File A memory", source_file="src/a.py")
    item2 = store.add(tier=MemoryTier.WORKING, content="File B memory", source_file="src/b.py")
    
    invalidator = MemoryInvalidator(session_id, db_path)
    count = invalidator.invalidate_stale_memories(["src/a.py"])
    
    assert count == 1
    
    item1_reloaded = store.get_by_id(item1.id)
    item2_reloaded = store.get_by_id(item2.id)
    
    assert item1_reloaded.is_valid == 0
    assert item2_reloaded.is_valid == 1


def test_invalidation_by_pattern_rule(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    
    item = store.add(
        tier=MemoryTier.TASK,
        content="Wildcard pattern memory",
        invalidation_rule={"type": "pattern", "pattern": "src/models/*.py"}
    )
    
    affected = invalidate_stale_memories(session_id, ["src/models/user.py"], db_path)
    assert affected == 1
    
    reloaded = store.get_by_id(item.id)
    assert reloaded.is_valid == 0

"""
Unit tests for TieredMemoryStore (memory/tiered_store.py)
"""

import pytest
import os
from tempfile import NamedTemporaryFile

from backend.repo_memory.db.database import init_db, close_db, get_db_session
from backend.repo_memory.db.models import SessionModel, MemoryTier
from backend.repo_memory.memory.tiered_store import TieredMemoryStore


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



def test_add_and_query_memory(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    
    item = store.add(
        tier=MemoryTier.WORKING,
        content="Testing working tier",
        source_file="test.py",
        confidence=0.9
    )
    assert item.id is not None
    assert item.tier == MemoryTier.WORKING.value
    
    results = store.query(tier=MemoryTier.WORKING)
    assert len(results) == 1
    assert results[0].content == "Testing working tier"


def test_batch_add(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    
    batch = [
        {"tier": MemoryTier.TASK, "content": "Task 1"},
        {"tier": MemoryTier.TASK, "content": "Task 2"},
        {"tier": MemoryTier.PROJECT, "content": "Project note"},
    ]
    created = store.add_batch(batch)
    assert len(created) == 3
    
    stats = store.get_stats()
    assert stats["total_items"] == 3


def test_update_and_delete_memory(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    
    item = store.add(tier=MemoryTier.PROCEDURAL, content="Original content")
    updated = store.update(item.id, content="Updated content", confidence=0.99)
    assert updated.content == "Updated content"
    assert updated.confidence == 0.99
    
    success = store.delete(item.id)
    assert success is True
    assert store.get_by_id(item.id) is None


def test_add_with_embedding(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    
    vec = [0.1, 0.2, 0.3, 0.4]
    item = store.add_with_embedding(
        tier=MemoryTier.EVIDENCE,
        content="Evidence with embedding",
        embedding_vector=vec
    )
    assert item.meta["embedding"] == vec
    
    embeddings_items = store.query_with_embeddings(tier=MemoryTier.EVIDENCE)
    assert len(embeddings_items) == 1

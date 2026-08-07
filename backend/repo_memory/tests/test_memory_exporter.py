"""
Unit tests for MemoryExporter (memory/memory_exporter.py)
"""

import pytest
import os
import json
from tempfile import NamedTemporaryFile

from backend.repo_memory.db.database import init_db, close_db, get_db_session
from backend.repo_memory.db.models import SessionModel, MemoryTier
from backend.repo_memory.memory.tiered_store import TieredMemoryStore
from backend.repo_memory.memory.memory_exporter import (
    MemoryExporter,
    export_memory_tier,
    import_memory,
)


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



def test_export_and_import_memory(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    
    store.add(tier=MemoryTier.WORKING, content="Export item 1")
    store.add(tier=MemoryTier.PROJECT, content="Export item 2")
    
    exporter = MemoryExporter(session_id, db_path)
    exported = exporter.export_memory_tier()
    assert len(exported) == 2
    
    # Import into second session
    with get_db_session(db_path) as session:
        session2 = SessionModel(repo_path="/fake/repo2", model_provider="test2")
        session.add(session2)
        session.commit()
        session2_id = session2.id
    
    imported = import_memory(session2_id, exported, db_path)
    assert len(imported) == 2
    
    store2 = TieredMemoryStore(session2_id, db_path)
    stats = store2.get_stats()
    assert stats["total_items"] == 2


def test_json_file_export_import(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    store.add(tier=MemoryTier.EPISODIC, content="JSON memory test")
    
    exporter = MemoryExporter(session_id, db_path)
    
    with NamedTemporaryFile(suffix=".json", delete=False) as json_tmp:
        json_path = json_tmp.name
    
    try:
        count = exporter.export_to_json(json_path)
        assert count == 1
        
        imported = exporter.import_from_json(json_path)
        assert len(imported) == 1
    finally:
        if os.path.exists(json_path):
            os.remove(json_path)


def test_clear_memory(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    store.add(tier=MemoryTier.WORKING, content="Clear working")
    store.add(tier=MemoryTier.TASK, content="Keep task")
    
    exporter = MemoryExporter(session_id, db_path)
    deleted = exporter.clear_memory(tier=MemoryTier.WORKING)
    assert deleted == 1
    
    remaining = store.query()
    assert len(remaining) == 1
    assert remaining[0].tier == MemoryTier.TASK.value

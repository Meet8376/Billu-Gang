"""
Unit tests for database layer
"""

import tempfile
from pathlib import Path
import pytest
from datetime import datetime, timezone

from backend.repo_memory.db import (
    init_db,
    close_db,
    get_db_session,
    SessionModel,
    MemoryItemModel,
    SymbolIndexModel,
    CallGraphEdgeModel,
)
from backend.repo_memory.db.models import MemoryTier


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    # Initialize database
    init_db(db_path, force_recreate=True)
    
    yield db_path
    
    # Cleanup
    close_db()
    try:
        Path(db_path).unlink(missing_ok=True)
    except PermissionError:
        pass



def test_init_db(temp_db):
    """Test database initialization"""
    assert Path(temp_db).exists()
    
    # Verify we can create a session
    with get_db_session(temp_db) as session:
        assert session is not None


def test_create_session(temp_db):
    """Test creating a session record"""
    with get_db_session(temp_db) as session:
        # Create session
        new_session = SessionModel(
            repo_path="/test/repo",
            model_provider="anthropic",
        )
        session.add(new_session)
        session.commit()
        
        # Verify
        assert new_session.id is not None
        assert new_session.started_at is not None


def test_create_memory_item(temp_db):
    """Test creating a memory item with provenance"""
    with get_db_session(temp_db) as session:
        # Create session first
        test_session = SessionModel(repo_path="/test/repo")
        session.add(test_session)
        session.flush()
        
        # Create memory item
        memory = MemoryItemModel(
            session_id=test_session.id,
            tier=MemoryTier.WORKING.value,
            content="Test memory item",
            source_file="test.py",
            source_line=10,
            confidence=0.95,
            invalidation_rule={"type": "file_change", "file": "test.py"},
        )
        session.add(memory)
        session.commit()
        
        # Verify
        assert memory.id is not None
        assert memory.tier == MemoryTier.WORKING.value
        assert memory.is_valid == 1
        assert memory.confidence == 0.95


def test_create_symbol_index(temp_db):
    """Test creating symbol index entries"""
    with get_db_session(temp_db) as session:
        # Create session
        test_session = SessionModel(repo_path="/test/repo")
        session.add(test_session)
        session.flush()
        
        # Create symbol
        symbol = SymbolIndexModel(
            session_id=test_session.id,
            file_path="test.py",
            symbol_name="test_function",
            symbol_type="function",
            language="python",
            start_line=1,
            end_line=5,
            signature="def test_function():",
        )
        session.add(symbol)
        session.commit()
        
        # Verify
        assert symbol.id is not None
        assert symbol.symbol_name == "test_function"
        assert symbol.language == "python"


def test_create_call_graph_edge(temp_db):
    """Test creating call graph edges"""
    with get_db_session(temp_db) as session:
        # Create session
        test_session = SessionModel(repo_path="/test/repo")
        session.add(test_session)
        session.flush()
        
        # Create edge
        edge = CallGraphEdgeModel(
            session_id=test_session.id,
            caller_file="caller.py",
            caller_symbol="caller_func",
            callee_file="callee.py",
            callee_symbol="callee_func",
            edge_type="call",
            confidence=1.0,
        )
        session.add(edge)
        session.commit()
        
        # Verify
        assert edge.id is not None
        assert edge.edge_type == "call"


def test_memory_tiers(temp_db):
    """Test all memory tier types"""
    with get_db_session(temp_db) as session:
        test_session = SessionModel(repo_path="/test/repo")
        session.add(test_session)
        session.flush()
        
        # Create memory item for each tier
        for tier in MemoryTier:
            memory = MemoryItemModel(
                session_id=test_session.id,
                tier=tier.value,
                content=f"Test content for {tier.value}",
            )
            session.add(memory)
        
        session.commit()
        
        # Verify all tiers were created
        memories = session.query(MemoryItemModel).filter_by(session_id=test_session.id).all()
        assert len(memories) == len(MemoryTier)
        
        tier_values = {m.tier for m in memories}
        assert tier_values == {t.value for t in MemoryTier}


def test_memory_invalidation(temp_db):
    """Test memory invalidation"""
    with get_db_session(temp_db) as session:
        test_session = SessionModel(repo_path="/test/repo")
        session.add(test_session)
        session.flush()
        
        # Create valid memory
        memory = MemoryItemModel(
            session_id=test_session.id,
            tier=MemoryTier.TASK.value,
            content="Valid memory",
            is_valid=1,
        )
        session.add(memory)
        session.commit()
        
        # Invalidate it
        memory.is_valid = 0
        memory.invalidated_at = datetime.now(timezone.utc)
        session.commit()
        
        # Verify
        assert memory.is_valid == 0
        assert memory.invalidated_at is not None


def test_session_relationships(temp_db):
    """Test relationships between session and other models"""
    with get_db_session(temp_db) as session:
        # Create session
        test_session = SessionModel(repo_path="/test/repo")
        session.add(test_session)
        session.flush()
        
        # Add related records
        memory = MemoryItemModel(
            session_id=test_session.id,
            tier=MemoryTier.WORKING.value,
            content="Test memory",
        )
        symbol = SymbolIndexModel(
            session_id=test_session.id,
            file_path="test.py",
            symbol_name="test_func",
            symbol_type="function",
            language="python",
            start_line=1,
            end_line=1,
        )
        
        session.add_all([memory, symbol])
        session.commit()
        
        # Verify relationships
        assert len(test_session.memory_items) == 1
        assert len(test_session.symbols) == 1
        assert test_session.memory_items[0].content == "Test memory"
        assert test_session.symbols[0].symbol_name == "test_func"

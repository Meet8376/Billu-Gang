"""
Unit tests for SymbolGraph (indexer/symbol_graph.py)
"""

import pytest
import os
from tempfile import NamedTemporaryFile

from backend.repo_memory.db.database import init_db, get_db_session
from backend.repo_memory.db.models import SessionModel, SymbolIndexModel
from backend.repo_memory.indexer.symbol_graph import SymbolGraph


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


def test_symbol_graph_init(temp_db):
    db_path, session_id = temp_db
    graph = SymbolGraph(session_id, db_path)
    stats = graph.get_stats()
    assert stats["nodes"] == 0
    assert stats["edges"] == 0


def test_add_symbol_and_dependency(temp_db):
    db_path, session_id = temp_db
    graph = SymbolGraph(session_id, db_path)
    
    graph.add_symbol("func_a", "file_a.py", "function")
    graph.add_symbol("func_b", "file_b.py", "function")
    
    graph.add_dependency(
        from_symbol="file_a.py::func_a",
        to_symbol="file_b.py::func_b",
        edge_type="call",
        confidence=0.9
    )
    
    stats = graph.get_stats()
    assert stats["nodes"] == 2
    assert stats["edges"] == 1


def test_get_callers_and_callees(temp_db):
    db_path, session_id = temp_db
    graph = SymbolGraph(session_id, db_path)
    
    graph.add_symbol("caller_fn", "a.py", "function")
    graph.add_symbol("callee_fn", "b.py", "function")
    
    graph.add_dependency("a.py::caller_fn", "b.py::callee_fn", "call")
    
    callers = graph.get_callers("callee_fn")
    assert len(callers) >= 1
    
    callees = graph.get_callees("caller_fn")
    assert len(callees) >= 1


def test_symbol_graph_save_and_load(temp_db):
    db_path, session_id = temp_db
    
    # Pre-populate DB with symbols so build_from_database works
    with get_db_session(db_path) as session:
        sym1 = SymbolIndexModel(
            session_id=session_id,
            file_path="main.py",
            symbol_name="my_func",
            symbol_type="function",
            language="python",
            start_line=1,
            end_line=10
        )
        sym2 = SymbolIndexModel(
            session_id=session_id,
            file_path="utils.py",
            symbol_name="helper_func",
            symbol_type="function",
            language="python",
            start_line=1,
            end_line=5
        )
        session.add(sym1)
        session.add(sym2)
        session.commit()

    graph = SymbolGraph(session_id, db_path)
    graph.add_symbol("my_func", "main.py", "function", start_line=1, end_line=10)
    graph.add_symbol("helper_func", "utils.py", "function", start_line=1, end_line=5)
    graph.add_dependency("main.py::my_func", "utils.py::helper_func", "call", confidence=0.95)
    
    graph.save()
    
    # Reload graph from DB
    graph2 = SymbolGraph(session_id, db_path)
    graph2.build_from_database()
    
    stats = graph2.get_stats()
    assert stats["nodes"] >= 2
    assert stats["edges"] >= 1

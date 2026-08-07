"""
Unit tests for MemoryAblationController (memory/ablation.py)
"""

import pytest
import os
from tempfile import NamedTemporaryFile

from backend.repo_memory.db.database import init_db, get_db_session
from backend.repo_memory.db.models import SessionModel, MemoryTier
from backend.repo_memory.memory.tiered_store import TieredMemoryStore
from backend.repo_memory.memory.ablation import MemoryAblationController, MemoryAblationMode


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


def test_warm_vs_cold_memory_ablation(temp_db):
    db_path, session_id = temp_db
    store = TieredMemoryStore(session_id, db_path)
    store.add(tier=MemoryTier.PROJECT, content="Ablation learned convention: Use fast JSON parser")

    ablation = MemoryAblationController(session_id, db_path)

    # 1. Warm Memory (Memory ON)
    warm_ctx = ablation.assemble_ablated_context(
        query="Help me write JSON parser",
        mode=MemoryAblationMode.WARM_MEMORY
    )
    assert warm_ctx["ablation_mode"] == "warm_memory"
    assert len(warm_ctx["included_memories"]) >= 1

    # 2. Cold Memory (Memory OFF)
    cold_ctx = ablation.assemble_ablated_context(
        query="Help me write JSON parser",
        mode=MemoryAblationMode.COLD_MEMORY
    )
    assert cold_ctx["ablation_mode"] == "cold_memory"
    assert len(cold_ctx["included_memories"]) == 0

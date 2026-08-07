"""
Unit tests for ContextLatencyProfiler (context/latency_profiler.py)
"""

import pytest
import os
from tempfile import NamedTemporaryFile

from backend.repo_memory.db.database import init_db, get_db_session
from backend.repo_memory.db.models import SessionModel
from backend.repo_memory.context.latency_profiler import ContextLatencyProfiler


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


def test_latency_profiling(temp_db):
    db_path, session_id = temp_db
    profiler = ContextLatencyProfiler(session_id, db_path)

    metrics = profiler.profile_assembly(
        query="Benchmark context latency",
        runs=2
    )

    assert "avg_latency_ms" in metrics
    assert metrics["runs"] == 2
    assert metrics["avg_latency_ms"] >= 0.0

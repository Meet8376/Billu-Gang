"""
Clean Database Initialization Script (FR1)

Initializes a fresh SQLite database, tables, and session for user onboarding (`harness init`).
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from .database import init_db, get_db_session
from .models import SessionModel
from ..indexer.file_scanner import scan_repository


def initialize_harness_repo_memory(
    repo_path: str,
    db_path: Optional[str] = None,
    model_provider: str = "default"
) -> Dict[str, Any]:
    """
    Initialize a fresh repo memory database and scan target repository.

    Args:
        repo_path: Path to target repository root
        db_path: Optional SQLite database file path (defaults to harness.db inside repo)
        model_provider: Name of LLM model provider

    Returns:
        Dictionary containing session info and scanned file stats
    """
    repo = Path(repo_path).resolve()
    if not repo.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    if db_path is None:
        db_path = str(repo / "harness.db")

    # Initialize SQLite database schema
    init_db(db_path, force_recreate=True)

    # Create new analysis session
    with get_db_session(db_path) as session:
        new_session = SessionModel(
            repo_path=str(repo),
            model_provider=model_provider,
            meta={"initialized_by": "harness_init"}
        )
        session.add(new_session)
        session.commit()
        session_id = new_session.id

    # Scan repository files
    files = scan_repository(str(repo))

    return {
        "status": "initialized",
        "session_id": session_id,
        "repo_path": str(repo),
        "db_path": db_path,
        "scanned_files_count": len(files),
    }

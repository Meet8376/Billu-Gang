"""
SQLAlchemy Database Engine & Session Management

Handles SQLite connection, session lifecycle, and database initialization.
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base

# Default database location: <repo_root>/harness.db
DEFAULT_DB_NAME = "harness.db"


def get_db_path(repo_root: str = None) -> str:
    """
    Get the database file path.
    
    Args:
        repo_root: Repository root directory. If None, uses current working directory.
        
    Returns:
        Absolute path to the SQLite database file
    """
    if repo_root is None:
        repo_root = os.getcwd()
    
    db_path = Path(repo_root) / DEFAULT_DB_NAME
    return str(db_path.absolute())


def create_db_engine(db_path: str = None, echo: bool = False):
    """
    Create SQLAlchemy engine for SQLite database.
    
    Args:
        db_path: Path to SQLite database file. If None, uses default location.
        echo: Whether to echo SQL queries (for debugging)
        
    Returns:
        SQLAlchemy Engine instance
    """
    if db_path is None:
        db_path = get_db_path()
    
    # Ensure parent directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine with SQLite-specific configuration
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=echo,
        connect_args={"check_same_thread": False},  # Allow multi-threaded access
        pool_pre_ping=True,  # Verify connections before use
    )
    
    return engine


# Global engine and session factory (initialized on first use)
engine = None
SessionLocal = None


def init_db(db_path: str = None, echo: bool = False, force_recreate: bool = False):
    """
    Initialize database schema and create all tables.
    
    Args:
        db_path: Path to SQLite database file
        echo: Whether to echo SQL queries
        force_recreate: If True, drop all tables and recreate
        
    Returns:
        SQLAlchemy Engine instance
    """
    global engine, SessionLocal
    
    if db_path is None:
        db_path = get_db_path()
    
    engine = create_db_engine(db_path, echo=echo)
    
    # Drop all tables if force recreate
    if force_recreate:
        Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )
    
    return engine


def close_db():
    """Dispose global database engine connection pool."""
    global engine, SessionLocal
    if engine is not None:
        engine.dispose()
        engine = None
        SessionLocal = None



@contextmanager
def get_db_session(db_path: str = None) -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db_session() as session:
            # Use session for queries
            session.query(...)
            session.commit()
    
    Args:
        db_path: Path to SQLite database file
        
    Yields:
        SQLAlchemy Session instance
    """
    global SessionLocal, engine
    
    # Initialize database if not already done
    if SessionLocal is None or engine is None:
        init_db(db_path)
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session_factory(db_path: str = None):
    """
    Get or create the global session factory.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        SQLAlchemy sessionmaker instance
    """
    global SessionLocal, engine
    
    if SessionLocal is None or engine is None:
        init_db(db_path)
    
    return SessionLocal

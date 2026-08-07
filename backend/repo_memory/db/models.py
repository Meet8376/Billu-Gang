"""
SQLAlchemy ORM Models

Database schema for tiered memory, repository index, and session state.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class MemoryTier(str, Enum):
    """Seven-tier memory hierarchy"""
    WORKING = "working"  # Current task working state
    TASK = "task"  # Task-specific context
    PROJECT = "project"  # Project conventions & patterns
    EPISODIC = "episodic"  # Past outcomes & learnings
    PROCEDURAL = "procedural"  # Reusable procedures
    PREFERENCE = "preference"  # User preferences
    EVIDENCE = "evidence"  # Verified evidence items


class SessionModel(Base):
    """Repository analysis session"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_path = Column(String(512), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    model_provider = Column(String(64), nullable=True)
    meta = Column(JSON, default=dict)

    # Relationships
    memory_items = relationship("MemoryItemModel", back_populates="session", cascade="all, delete-orphan")
    symbols = relationship("SymbolIndexModel", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id={self.id}, repo_path={self.repo_path})>"


class MemoryItemModel(Base):
    """Tiered memory item with provenance"""
    __tablename__ = "memory_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    tier = Column(String(32), nullable=False)  # MemoryTier enum value
    content = Column(Text, nullable=False)
    
    # Provenance tracking
    source_file = Column(String(512), nullable=True)  # Origin file path
    source_line = Column(Integer, nullable=True)  # Line number in source
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(128), nullable=True)  # Model ID that created this
    confidence = Column(Float, default=1.0)  # Confidence score (0-1)
    
    # Invalidation rules
    invalidation_rule = Column(JSON, default=dict)  # Rule for when to invalidate
    invalidated_at = Column(DateTime, nullable=True)
    is_valid = Column(Integer, default=1)  # Boolean: 1=valid, 0=invalid
    
    # Metadata
    meta = Column(JSON, default=dict)
    embedding = Column(JSON, nullable=True)  # For semantic search

    # Relationships
    session = relationship("SessionModel", back_populates="memory_items")

    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_session_tier", "session_id", "tier"),
        Index("idx_valid_tier", "is_valid", "tier"),
        Index("idx_source_file", "source_file"),
    )

    def __repr__(self):
        return f"<MemoryItem(id={self.id}, tier={self.tier}, valid={self.is_valid})>"


class SymbolIndexModel(Base):
    """Polyglot symbol index for functions, classes, methods"""
    __tablename__ = "symbol_index"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    
    # Symbol identification
    file_path = Column(String(512), nullable=False)
    symbol_name = Column(String(256), nullable=False)
    symbol_type = Column(String(32), nullable=False)  # function, class, method, variable
    language = Column(String(32), nullable=False)  # python, typescript, javascript
    
    # Location
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    start_col = Column(Integer, nullable=True)
    end_col = Column(Integer, nullable=True)
    
    # Symbol details
    parent_symbol = Column(String(256), nullable=True)  # For methods: parent class
    signature = Column(Text, nullable=True)  # Function signature
    docstring = Column(Text, nullable=True)
    
    # Metadata
    indexed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_hash = Column(String(64), nullable=True)  # For invalidation detection
    meta = Column(JSON, default=dict)

    # Relationships
    session = relationship("SessionModel", back_populates="symbols")

    # Indexes
    __table_args__ = (
        Index("idx_session_file", "session_id", "file_path"),
        Index("idx_symbol_name", "symbol_name"),
        Index("idx_file_symbol", "file_path", "symbol_name"),
    )

    def __repr__(self):
        return f"<Symbol(name={self.symbol_name}, type={self.symbol_type}, file={self.file_path})>"


class CallGraphEdgeModel(Base):
    """Directed call graph edge representing dependencies"""
    __tablename__ = "call_graph"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    
    # Edge definition: caller -> callee
    caller_file = Column(String(512), nullable=False)
    caller_symbol = Column(String(256), nullable=False)
    callee_file = Column(String(512), nullable=False)
    callee_symbol = Column(String(256), nullable=False)
    
    # Edge metadata
    edge_type = Column(String(32), nullable=False)  # call, import, inheritance
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    meta = Column(JSON, default=dict)

    # Indexes
    __table_args__ = (
        Index("idx_caller", "session_id", "caller_file", "caller_symbol"),
        Index("idx_callee", "session_id", "callee_file", "callee_symbol"),
    )

    def __repr__(self):
        return f"<CallEdge({self.caller_symbol} -> {self.callee_symbol})>"

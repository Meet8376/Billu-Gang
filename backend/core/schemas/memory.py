"""
Tiered Memory Pydantic v2 Schemas.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class MemoryTier(str, Enum):
    CORE_SPEC = "core_spec"
    WORKSPACE_INDEX = "workspace_index"
    CONTEXT_SESSION = "context_session"
    EPHEMERAL_SCRATCH = "ephemeral_scratch"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    TASK = "task"
    PROJECT = "project"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    PREFERENCE = "preference"
    EVIDENCE = "evidence"


class ProvenanceMetadata(BaseModel):
    """Provenance tracking details for a memory item."""
    source_file: Optional[str] = None
    line_range: Optional[str] = None
    extracted_by: str = "ast_scanner"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryItem(BaseModel):
    """Structure for a stored memory item."""
    id: str
    tier: MemoryTier
    key: Optional[str] = ""
    content: str
    provenance: ProvenanceMetadata = Field(default_factory=ProvenanceMetadata)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    invalidated: bool = False

"""
Tiered Memory Pydantic v2 Schemas.
Member 2 — Backend Core & Model Adapter Lead
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class MemoryTier(str, Enum):
    CORE_SPEC = "core_spec"
    WORKSPACE_INDEX = "workspace_index"
    CONTEXT_SESSION = "context_session"
    EPHEMERAL_SCRATCH = "ephemeral_scratch"


class ProvenanceMetadata(BaseModel):
    """Provenance tracking details for a memory item."""
    source_file: Optional[str] = None
    line_range: Optional[str] = None
    extracted_by: str = "ast_scanner"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MemoryItem(BaseModel):
    """Structure for a stored memory item."""
    id: str
    tier: MemoryTier
    key: str
    content: str
    provenance: ProvenanceMetadata = Field(default_factory=ProvenanceMetadata)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    invalidated: bool = False

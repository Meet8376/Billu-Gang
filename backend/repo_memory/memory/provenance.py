"""
Provenance Management for Tiered Memory Items

Attaches metadata (source file line, timestamp, author model, confidence score)
to memories and provides provenance tracking and validation.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict


@dataclass
class ProvenanceRecord:
    """
    Metadata provenance record for a memory item.
    """
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    created_by: Optional[str] = None
    confidence: float = 1.0
    timestamp: str = ""
    meta: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.meta is None:
            self.meta = {}


def create_provenance_record(
    source_file: Optional[str] = None,
    source_line: Optional[int] = None,
    created_by: Optional[str] = None,
    confidence: float = 1.0,
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a metadata provenance dictionary for attaching to a MemoryItem.

    Args:
        source_file: Path to source file
        source_line: Line number in source file
        created_by: Identifier of the model or system creating the memory
        confidence: Confidence score (0.0 to 1.0)
        meta: Additional metadata dict

    Returns:
        Provenance dictionary
    """
    record = ProvenanceRecord(
        source_file=source_file,
        source_line=source_line,
        created_by=created_by,
        confidence=confidence,
        meta=meta or {}
    )
    return asdict(record)


def validate_provenance(record: Dict[str, Any]) -> bool:
    """
    Validate that a provenance record contains valid fields.

    Args:
        record: Provenance dictionary

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(record, dict):
        return False
    
    confidence = record.get("confidence", 1.0)
    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        return False

    return True

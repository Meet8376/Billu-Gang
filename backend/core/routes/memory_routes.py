"""
Tiered Memory Route Handlers (With Security Credential Redaction).
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import List, Optional
from fastapi import APIRouter, status, Query

from backend.core.schemas.memory import MemoryItem, MemoryTier
from backend.core.security import CredentialSanitizer

router = APIRouter()

# In-memory storage stub for tiered memory items
_memory_store: List[MemoryItem] = []


@router.get(
    "/memory",
    response_model=List[MemoryItem],
    summary="Retrieve Tiered Memory Items",
    description="Retrieve stored memory items from short-term, medium-term, or long-term tiers. Filter by tier if specified.",
)
async def get_memory(
    tier: Optional[MemoryTier] = Query(None, description="Optional memory tier filter (short_term, medium_term, long_term)")
) -> List[MemoryItem]:
    """Retrieve memory items, optionally filtered by tier."""
    if tier:
        return [item for item in _memory_store if item.tier == tier and not item.invalidated]
    return [item for item in _memory_store if not item.invalidated]


@router.post(
    "/memory",
    response_model=MemoryItem,
    status_code=status.HTTP_201_CREATED,
    summary="Add Memory Item",
    description="Add a new item to tiered memory. Automatically redacts API keys, passwords, or tokens from item content and metadata.",
)
async def add_memory_item(item: MemoryItem) -> MemoryItem:
    """Add a new item to tiered memory with security credential redaction."""
    clean_content, _ = CredentialSanitizer.sanitize_text(item.content)
    clean_metadata = item.metadata
    if item.metadata:
        sanitized_dict, _ = CredentialSanitizer.sanitize_payload(item.metadata.model_dump())
        clean_metadata = item.metadata.model_validate(sanitized_dict)

    sanitized_item = MemoryItem(
        id=item.id,
        tier=item.tier,
        key=item.key,
        content=clean_content,
        provenance=item.provenance,
        invalidated=item.invalidated,
        metadata=clean_metadata,
    )
    _memory_store.append(sanitized_item)
    return sanitized_item


@router.delete(
    "/memory/wipe",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Wipe All Memory Storage",
    description="Clear all stored memory items across all tiers.",
)
async def wipe_memory():
    """Wipe all stored memory items."""
    _memory_store.clear()

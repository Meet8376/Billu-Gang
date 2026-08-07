"""
Tiered Memory Route Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import List, Optional
from fastapi import APIRouter, status, Query

from backend.core.schemas.memory import MemoryItem, MemoryTier

router = APIRouter()

# In-memory storage stub
_memory_store: List[MemoryItem] = []


@router.get("/memory", response_model=List[MemoryItem])
async def get_memory(tier: Optional[MemoryTier] = Query(None)):
    """Retrieve memory items, optionally filtered by tier."""
    if tier:
        return [item for item in _memory_store if item.tier == tier and not item.invalidated]
    return [item for item in _memory_store if not item.invalidated]


@router.post("/memory", response_model=MemoryItem, status_code=status.HTTP_201_CREATED)
async def add_memory_item(item: MemoryItem):
    """Add a new item to tiered memory."""
    _memory_store.append(item)
    return item


@router.delete("/memory/wipe", status_code=status.HTTP_204_NO_CONTENT)
async def wipe_memory():
    """Wipe all stored memory items."""
    _memory_store.clear()

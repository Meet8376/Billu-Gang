"""
Memory Serializer / Exporter

Exports memory store tiers to JSON / dictionary formats and imports/rehydrates
memory stores during benchmark replays or session migrations.
"""

from typing import List, Dict, Optional, Any, Union
import json
from datetime import datetime

from ..db.database import get_db_session
from ..db.models import MemoryItemModel, MemoryTier
from .tiered_store import TieredMemoryStore


class MemoryExporter:
    """
    Export, import, and reset memory tiers for a session.
    """

    def __init__(self, session_id: int, db_path: Optional[str] = None):
        self.session_id = session_id
        self.db_path = db_path
        self.store = TieredMemoryStore(session_id, db_path)

    def export_memory_tier(
        self,
        tier: Optional[Union[MemoryTier, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Export memory items for a specific tier (or all tiers) as a list of dicts.

        Args:
            tier: Optional MemoryTier enum or tier name string

        Returns:
            List of serialized memory item dicts
        """
        tier_enum = None
        if tier is not None:
            if isinstance(tier, str):
                tier_enum = MemoryTier(tier)
            else:
                tier_enum = tier

        items = self.store.query(tier=tier_enum, is_valid=None)
        
        exported = []
        for item in items:
            exported.append({
                "id": item.id,
                "session_id": item.session_id,
                "tier": item.tier,
                "content": item.content,
                "source_file": item.source_file,
                "source_line": item.source_line,
                "created_by": item.created_by,
                "confidence": item.confidence,
                "is_valid": bool(item.is_valid),
                "invalidation_rule": item.invalidation_rule,
                "meta": item.meta,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "invalidated_at": item.invalidated_at.isoformat() if item.invalidated_at else None,
            })
        return exported

    def export_to_json(self, file_path: str, tier: Optional[Union[MemoryTier, str]] = None) -> int:
        """
        Export memory items to a JSON file.

        Args:
            file_path: Target JSON file path
            tier: Optional tier filter

        Returns:
            Count of exported items
        """
        data = self.export_memory_tier(tier)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return len(data)

    def import_memory(self, items_data: List[Dict[str, Any]]) -> List[MemoryItemModel]:
        """
        Import memory item dictionaries into current session.

        Args:
            items_data: List of dicts representing memory items

        Returns:
            List of created MemoryItemModel instances
        """
        imported_items = []
        for data in items_data:
            tier_val = data.get("tier")
            if isinstance(tier_val, str):
                tier_enum = MemoryTier(tier_val)
            else:
                tier_enum = tier_val

            item = self.store.add(
                tier=tier_enum,
                content=data.get("content", ""),
                source_file=data.get("source_file"),
                source_line=data.get("source_line"),
                created_by=data.get("created_by"),
                confidence=data.get("confidence", 1.0),
                invalidation_rule=data.get("invalidation_rule"),
                meta=data.get("meta")
            )
            imported_items.append(item)
        return imported_items

    def import_from_json(self, file_path: str) -> List[MemoryItemModel]:
        """
        Import memory items from a JSON file.

        Args:
            file_path: Source JSON file path

        Returns:
            List of imported MemoryItemModel instances
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.import_memory(data)

    def clear_memory(self, tier: Optional[Union[MemoryTier, str]] = None) -> int:
        """
        Clear memory items in current session (optionally filtered by tier).

        Args:
            tier: Tier to clear (or None for all tiers)

        Returns:
            Count of deleted items
        """
        with get_db_session(self.db_path) as session:
            query = session.query(MemoryItemModel).filter_by(session_id=self.session_id)
            if tier is not None:
                tier_val = tier.value if isinstance(tier, MemoryTier) else tier
                query = query.filter_by(tier=tier_val)
            
            count = query.delete(synchronize_session=False)
            session.commit()
            return count


def export_memory_tier(
    session_id: int,
    tier: Optional[Union[MemoryTier, str]] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convenience export function.
    """
    exporter = MemoryExporter(session_id, db_path)
    return exporter.export_memory_tier(tier)


def import_memory(
    session_id: int,
    items_data: List[Dict[str, Any]],
    db_path: Optional[str] = None
) -> List[MemoryItemModel]:
    """
    Convenience import function.
    """
    exporter = MemoryExporter(session_id, db_path)
    return exporter.import_memory(items_data)

"""
Memory Invalidation Engine

Automatically flags or invalidates memory items when target files are updated or deleted.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import fnmatch

from ..db.database import get_db_session
from ..db.models import MemoryItemModel
from .tiered_store import TieredMemoryStore


class MemoryInvalidator:
    """
    Engine for checking and executing automatic memory invalidation when workspace files change.
    """

    def __init__(self, session_id: int, db_path: Optional[str] = None):
        self.session_id = session_id
        self.db_path = db_path
        self.store = TieredMemoryStore(session_id, db_path)

    def invalidate_stale_memories(self, modified_files: List[str]) -> int:
        """
        Invalidate all memory items in the current session associated with modified files.

        Args:
            modified_files: List of file paths that were modified or deleted.

        Returns:
            Count of invalidated items.
        """
        if not modified_files:
            return 0
            
        return self.store.invalidate_batch(modified_files)

    def check_file_mutation(self, file_path: str) -> List[MemoryItemModel]:
        """
        Find memory items that would be invalidated if a file is modified.

        Args:
            file_path: File path to check

        Returns:
            List of MemoryItemModel objects affected
        """
        with get_db_session(self.db_path) as session:
            items = session.query(MemoryItemModel)\
                .filter_by(session_id=self.session_id, is_valid=1)\
                .all()
            
            affected = []
            for item in items:
                if item.source_file == file_path:
                    affected.append(item)
                elif item.invalidation_rule:
                    rule = item.invalidation_rule
                    rule_type = rule.get("type")
                    if rule_type == "file_change" and rule.get("file") == file_path:
                        affected.append(item)
                    elif rule_type == "pattern" and fnmatch.fnmatch(file_path, rule.get("pattern", "")):
                        affected.append(item)
            return affected


def invalidate_stale_memories(
    session_id: int,
    modified_files: List[str],
    db_path: Optional[str] = None
) -> int:
    """
    Convenience function to invalidate stale memories for a session.

    Args:
        session_id: Session ID
        modified_files: List of modified file paths
        db_path: Optional database path

    Returns:
        Count of invalidated items
    """
    invalidator = MemoryInvalidator(session_id, db_path)
    return invalidator.invalidate_stale_memories(modified_files)

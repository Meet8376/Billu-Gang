"""
Tiered Memory Store - CRUD Engine for 7-Tier Memory

Manages memory items across Working, Task, Project, Episodic, Procedural,
Preference, and Evidence tiers with provenance tracking and invalidation.
"""

from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime, timezone, timedelta
import fnmatch

from sqlalchemy.orm import Session

from ..db.database import get_db_session
from ..db.models import MemoryItemModel, MemoryTier, SessionModel


class TieredMemoryStore:
    """
    CRUD engine for 7-tier memory system.
    
    Attributes:
        session_id: Current database session ID
        db_path: Optional path to database file
    """
    
    def __init__(self, session_id: int, db_path: Optional[str] = None):
        """
        Initialize memory store for a session.
        
        Args:
            session_id: Database session ID
            db_path: Optional path to database file
        """
        self.session_id = session_id
        self.db_path = db_path
    
    def add(
        self,
        tier: MemoryTier,
        content: str,
        source_file: Optional[str] = None,
        source_line: Optional[int] = None,
        created_by: Optional[str] = None,
        confidence: float = 1.0,
        invalidation_rule: Optional[Dict] = None,
        meta: Optional[Dict] = None
    ) -> MemoryItemModel:
        """
        Create new memory item.
        
        Args:
            tier: Memory tier (Working, Task, Project, etc.)
            content: Memory content text
            source_file: Optional source file path
            source_line: Optional source line number
            created_by: Optional model ID that created this
            confidence: Confidence score (0.0-1.0)
            invalidation_rule: Optional invalidation rule as dict
            meta: Optional metadata dict
        
        Returns:
            Created MemoryItemModel
        
        Requirement: 4.2, 6
        """
        with get_db_session(self.db_path) as session:
            memory = MemoryItemModel(
                session_id=self.session_id,
                tier=tier.value,
                content=content,
                source_file=source_file,
                source_line=source_line,
                created_by=created_by,
                confidence=confidence,
                invalidation_rule=invalidation_rule or {},
                meta=meta or {},
                is_valid=1
            )
            
            session.add(memory)
            session.commit()
            session.refresh(memory)
            
            return memory
    
    def add_batch(self, items: List[Dict]) -> List[MemoryItemModel]:
        """
        Bulk create memory items in single transaction.
        
        Args:
            items: List of dictionaries with memory item parameters
        
        Returns:
            List of created MemoryItemModel objects
        
        Requirement: 5.1
        """
        with get_db_session(self.db_path) as session:
            memories = []
            
            for item_data in items:
                # Extract tier (required)
                tier = item_data.get('tier')
                if isinstance(tier, str):
                    tier = MemoryTier(tier)
                
                memory = MemoryItemModel(
                    session_id=self.session_id,
                    tier=tier.value,
                    content=item_data.get('content', ''),
                    source_file=item_data.get('source_file'),
                    source_line=item_data.get('source_line'),
                    created_by=item_data.get('created_by'),
                    confidence=item_data.get('confidence', 1.0),
                    invalidation_rule=item_data.get('invalidation_rule', {}),
                    meta=item_data.get('meta', {}),
                    is_valid=1
                )
                session.add(memory)
                memories.append(memory)
            
            session.commit()
            
            # Refresh all to get IDs
            for memory in memories:
                session.refresh(memory)
            
            return memories
    
    def query(
        self,
        tier: Optional[Union[MemoryTier, List[MemoryTier]]] = None,
        source_file: Optional[str] = None,
        is_valid: Optional[bool] = True,
        confidence_threshold: Optional[float] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        limit: Optional[int] = None
    ) -> List[MemoryItemModel]:
        """
        Query memory items with complex filters.
        
        Args:
            tier: Single tier or list of tiers to filter by
            source_file: Source file path (supports wildcards)
            is_valid: Filter by validity status (None = both)
            confidence_threshold: Minimum confidence score
            date_range: Tuple of (start_date, end_date)
            limit: Maximum number of results
        
        Returns:
            List of matching MemoryItemModel objects
        
        Requirement: 4.3, 13
        """
        with get_db_session(self.db_path) as session:
            # Start with base query for this session
            query = session.query(MemoryItemModel)\
                .filter_by(session_id=self.session_id)
            
            # Apply tier filter
            if tier is not None:
                if isinstance(tier, list):
                    tier_values = [t.value for t in tier]
                    query = query.filter(MemoryItemModel.tier.in_(tier_values))
                else:
                    query = query.filter_by(tier=tier.value)
            
            # Apply source file filter
            if source_file:
                if '*' in source_file or '?' in source_file:
                    # Wildcard pattern - use Python filtering after query
                    pass  # Handle after fetching
                else:
                    query = query.filter_by(source_file=source_file)
            
            # Apply validity filter
            if is_valid is not None:
                query = query.filter_by(is_valid=1 if is_valid else 0)
            
            # Apply confidence threshold
            if confidence_threshold is not None:
                query = query.filter(MemoryItemModel.confidence >= confidence_threshold)
            
            # Apply date range
            if date_range:
                start, end = date_range
                query = query.filter(
                    MemoryItemModel.created_at.between(start, end)
                )
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            
            # Post-filter for wildcard patterns
            if source_file and ('*' in source_file or '?' in source_file):
                results = [
                    r for r in results
                    if r.source_file and fnmatch.fnmatch(r.source_file, source_file)
                ]
            
            return results
    
    def get_by_id(self, memory_id: int) -> Optional[MemoryItemModel]:
        """
        Retrieve single memory item by ID.
        
        Args:
            memory_id: Memory item ID
        
        Returns:
            MemoryItemModel or None if not found
        
        Requirement: 4.6
        """
        with get_db_session(self.db_path) as session:
            memory = session.query(MemoryItemModel)\
                .filter_by(id=memory_id, session_id=self.session_id)\
                .first()
            return memory
    
    def update(self, memory_id: int, **updates) -> Optional[MemoryItemModel]:
        """
        Modify existing memory item.
        
        Args:
            memory_id: Memory item ID
            **updates: Fields to update
        
        Returns:
            Updated MemoryItemModel or None if not found
        
        Requirement: 4.4
        """
        with get_db_session(self.db_path) as session:
            memory = session.query(MemoryItemModel)\
                .filter_by(id=memory_id, session_id=self.session_id)\
                .first()
            
            if not memory:
                return None
            
            # Update fields
            for key, value in updates.items():
                if hasattr(memory, key):
                    setattr(memory, key, value)
            
            session.commit()
            session.refresh(memory)
            return memory
    
    def delete(self, memory_id: int) -> bool:
        """
        Permanently remove memory item.
        
        Args:
            memory_id: Memory item ID
        
        Returns:
            True if deleted, False if not found
        
        Requirement: 4.5
        """
        with get_db_session(self.db_path) as session:
            memory = session.query(MemoryItemModel)\
                .filter_by(id=memory_id, session_id=self.session_id)\
                .first()
            
            if not memory:
                return False
            
            session.delete(memory)
            session.commit()
            return True
    
    def invalidate_batch(self, source_files: List[str]) -> int:
        """
        Mark memory items as invalid for modified files.
        
        Args:
            source_files: List of modified file paths
        
        Returns:
            Count of invalidated items
        
        Requirement: 5.3, 7
        """
        count = 0
        
        with get_db_session(self.db_path) as session:
            # Get all valid items for this session
            items = session.query(MemoryItemModel)\
                .filter_by(session_id=self.session_id, is_valid=1)\
                .all()
            
            for item in items:
                if self.check_validity(item.id, source_files, session):
                    item.is_valid = 0
                    item.invalidated_at = datetime.now(timezone.utc)
                    count += 1
            
            session.commit()
        
        return count
    
    def check_validity(
        self,
        memory_id: int,
        modified_files: List[str],
        session: Optional[Session] = None
    ) -> bool:
        """
        Check if memory item should be invalidated.
        
        Args:
            memory_id: Memory item ID
            modified_files: List of modified file paths
            session: Optional existing session
        
        Returns:
            True if item should be invalidated
        
        Requirement: 7.3
        """
        def _check(sess):
            item = sess.query(MemoryItemModel)\
                .filter_by(id=memory_id)\
                .first()
            
            if not item:
                return False
            
            rule = item.invalidation_rule
            rule_type = rule.get("type")
            
            # Check file_change rule
            if rule_type == "file_change":
                target_file = rule.get("file")
                if target_file in modified_files:
                    return True
            
            # Check pattern rule (wildcard matching)
            elif rule_type == "pattern":
                pattern = rule.get("pattern")
                for modified_file in modified_files:
                    if fnmatch.fnmatch(modified_file, pattern):
                        return True
            
            # Check direct source_file match
            if item.source_file and item.source_file in modified_files:
                return True
            
            return False
        
        if session:
            return _check(session)
        else:
            with get_db_session(self.db_path) as sess:
                return _check(sess)
    
    def compact(self, older_than_days: int = 7) -> int:
        """
        Remove old invalid memory items.
        
        Args:
            older_than_days: Remove items invalidated more than this many days ago
        
        Returns:
            Count of removed items
        
        Requirement: 5.5
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        
        with get_db_session(self.db_path) as session:
            # Query old invalid items
            result = session.query(MemoryItemModel)\
                .filter_by(session_id=self.session_id, is_valid=0)\
                .filter(MemoryItemModel.invalidated_at < cutoff_date)\
                .delete()
            
            session.commit()
            return result
    
    def add_with_embedding(
        self,
        tier: MemoryTier,
        content: str,
        embedding_vector: List[float],
        **kwargs
    ) -> MemoryItemModel:
        """
        Add memory item with vector embedding.
        
        Args:
            tier: Memory tier
            content: Memory content
            embedding_vector: Vector embedding as list of floats
            **kwargs: Additional parameters for add()
        
        Returns:
            Created MemoryItemModel
        
        Requirement: 20
        """
        # Validate embedding is numeric array
        if not all(isinstance(x, (int, float)) for x in embedding_vector):
            raise ValueError("Embedding vector must contain only numeric values")
        
        # Store embedding as JSON
        kwargs['meta'] = kwargs.get('meta', {})
        kwargs['meta']['embedding'] = embedding_vector
        
        return self.add(tier, content, **kwargs)
    
    def query_with_embeddings(
        self,
        tier: Optional[MemoryTier] = None,
        filters: Optional[Dict] = None
    ) -> List[MemoryItemModel]:
        """
        Retrieve memory items with their embeddings.
        
        Args:
            tier: Optional tier to filter by
            filters: Optional additional filters
        
        Returns:
            List of MemoryItemModel objects that have embeddings
        
        Requirement: 20.4
        """
        filters = filters or {}
        filters['tier'] = tier
        
        # Query items
        items = self.query(**filters)
        
        # Filter to only items with embeddings
        items_with_embeddings = [
            item for item in items
            if item.meta and 'embedding' in item.meta
        ]
        
        return items_with_embeddings
    
    def query_all_sessions(
        self,
        tier: Optional[MemoryTier] = None,
        filters: Optional[Dict] = None
    ) -> List[MemoryItemModel]:
        """
        Query memory items across all sessions.
        
        Args:
            tier: Optional tier to filter by
            filters: Optional additional filters
        
        Returns:
            List of MemoryItemModel objects from all sessions
        
        Requirement: 17.3
        """
        with get_db_session(self.db_path) as session:
            query = session.query(MemoryItemModel)
            
            if tier:
                query = query.filter_by(tier=tier.value)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(MemoryItemModel, key):
                        query = query.filter_by(**{key: value})
            
            return query.all()
    
    def get_stats(self) -> Dict:
        """
        Get statistics about memory store.
        
        Returns:
            Dictionary with counts by tier and validity
        """
        with get_db_session(self.db_path) as session:
            total = session.query(MemoryItemModel)\
                .filter_by(session_id=self.session_id)\
                .count()
            
            valid = session.query(MemoryItemModel)\
                .filter_by(session_id=self.session_id, is_valid=1)\
                .count()
            
            # Count by tier
            tier_counts = {}
            for tier in MemoryTier:
                count = session.query(MemoryItemModel)\
                    .filter_by(session_id=self.session_id, tier=tier.value)\
                    .count()
                tier_counts[tier.value] = count
            
            return {
                'session_id': self.session_id,
                'total_items': total,
                'valid_items': valid,
                'invalid_items': total - valid,
                'tier_counts': tier_counts
            }

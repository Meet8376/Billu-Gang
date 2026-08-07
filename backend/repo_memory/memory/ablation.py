"""
Memory Ablation Controller (NFR30)

Supports deterministic, reproducible benchmark runs for memory ablations:
- WARM_MEMORY (Memory ON): Context window includes tiered memories & learned patterns.
- COLD_MEMORY (Memory OFF): Context window excludes past memories for cold-start comparison.
"""

from enum import Enum
from typing import Dict, Any, Optional, List

from ..context.context_manager import ContextManager


class MemoryAblationMode(str, Enum):
    WARM_MEMORY = "warm_memory"  # Memory ON
    COLD_MEMORY = "cold_memory"  # Memory OFF


class MemoryAblationController:
    """
    Controls memory retrieval ablation modes for benchmarking harness performance.
    """

    def __init__(self, session_id: int, db_path: Optional[str] = None):
        self.session_id = session_id
        self.db_path = db_path
        self.context_manager = ContextManager(session_id, db_path)

    def assemble_ablated_context(
        self,
        query: str,
        mode: MemoryAblationMode = MemoryAblationMode.WARM_MEMORY,
        max_tokens: Optional[int] = None,
        file_paths: Optional[List[str]] = None,
        system_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assemble prompt context under specified ablation mode.

        Args:
            query: User query or coding task
            mode: WARM_MEMORY or COLD_MEMORY
            max_tokens: Token budget limit
            file_paths: List of file paths
            system_instructions: Base system prompt

        Returns:
            Assembled context dictionary
        """
        if mode == MemoryAblationMode.COLD_MEMORY:
            # Memory OFF: temporariliy pass no query memories
            result = self.context_manager.assemble_context(
                query=query,
                max_tokens=max_tokens,
                file_paths=file_paths,
                system_instructions=system_instructions
            )
            # Purge memory section from returned prompt
            result["included_memories"] = []
            result["ablation_mode"] = mode.value
            return result
        else:
            # Memory ON
            result = self.context_manager.assemble_context(
                query=query,
                max_tokens=max_tokens,
                file_paths=file_paths,
                system_instructions=system_instructions
            )
            result["ablation_mode"] = mode.value
            return result

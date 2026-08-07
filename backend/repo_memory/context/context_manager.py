"""
Context Manager - Token-Budgeted Context Window Assembler

Orchestrates prompt context assembly for LLM models:
- Budgets context window token limits (FR15)
- Ranks candidate memories and symbol graphs by semantic relevance
- Sanitizes prompt injections and secret credentials (FR17)
- Summarizes oversized files when token budget is exceeded
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None

from ..memory.tiered_store import TieredMemoryStore
from ..memory.invalidation import MemoryInvalidator
from ..indexer.symbol_graph import SymbolGraph
from .sanitizer import Sanitizer
from .relevance_ranker import RelevanceRanker
from .summarizer import FileSummarizer


class ContextManager:
    """
    Assembles sanitized, relevance-ranked, token-budgeted prompt context windows.
    """

    def __init__(
        self,
        session_id: int,
        db_path: Optional[str] = None,
        default_max_tokens: int = 4096,
        model_name: str = "gpt-4"
    ):
        self.session_id = session_id
        self.db_path = db_path
        self.default_max_tokens = default_max_tokens
        self.model_name = model_name

        self.memory_store = TieredMemoryStore(session_id, db_path)
        self.invalidator = MemoryInvalidator(session_id, db_path)
        self.symbol_graph = SymbolGraph(session_id, db_path)
        self.ranker = RelevanceRanker()
        self.sanitizer = Sanitizer()
        self.summarizer = FileSummarizer()

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text using tiktoken or fallback heuristic"""
        if not text:
            return 0
        if TIKTOKEN_AVAILABLE:
            try:
                enc = tiktoken.encoding_for_model(self.model_name)
                return len(enc.encode(text))
            except Exception:
                pass
        # Fallback: ~4 chars per token average
        return max(1, len(text) // 4)

    def assemble_context(
        self,
        query: str,
        max_tokens: Optional[int] = None,
        file_paths: Optional[List[str]] = None,
        system_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assemble a complete token-budgeted prompt context package.

        Args:
            query: User objective or coding issue query
            max_tokens: Context window token limit (defaults to self.default_max_tokens)
            file_paths: Target file paths to include
            system_instructions: Optional base system prompt

        Returns:
            Dictionary containing:
            - 'prompt': Formatted, sanitized, token-budgeted prompt string
            - 'token_count': Total estimated tokens
            - 'included_memories': List of memory items included
            - 'included_files': List of file previews/summaries included
            - 'sanitized_query': Query after injection/secret neutralization
        """
        budget = max_tokens if max_tokens is not None else self.default_max_tokens

        # 1. Sanitize user query and system instructions
        clean_query = self.sanitizer.sanitize(query)
        clean_system = self.sanitizer.sanitize(system_instructions) if system_instructions else "You are an expert pair-programmer AI."

        # Reserve tokens for base prompt shell
        base_shell_tokens = self.estimate_tokens(clean_system) + self.estimate_tokens(clean_query) + 200
        remaining_budget = max(500, budget - base_shell_tokens)

        prompt_sections = []
        included_memories = []
        included_files = []

        # 2. Retrieve valid memories across tiers
        all_memories = self.memory_store.query(is_valid=1)
        
        # 3. Rank memories by semantic relevance
        if all_memories:
            mem_dicts = [
                {
                    "id": m.id,
                    "tier": m.tier,
                    "content": m.content,
                    "source_file": m.source_file,
                    "confidence": m.confidence,
                }
                for m in all_memories
            ]
            ranked_mems = self.ranker.rank_items(clean_query, mem_dicts, text_key="content")
            
            memory_tokens_used = 0
            memory_section_lines = ["## Relevant Memory & Project Conventions:"]

            for mem in ranked_mems:
                mem_text = f"-[{mem['tier'].upper()}] {mem['content']}"
                mem_tokens = self.estimate_tokens(mem_text)
                
                # Check half of remaining budget for memories
                if memory_tokens_used + mem_tokens > (remaining_budget // 2):
                    break
                
                memory_section_lines.append(mem_text)
                memory_tokens_used += mem_tokens
                included_memories.append(mem)

            if len(memory_section_lines) > 1:
                prompt_sections.append("\n".join(memory_section_lines))
                remaining_budget -= memory_tokens_used

        # 4. Include relevant file previews or summaries
        if file_paths:
            file_section_lines = ["## Target Code Files:"]
            for fp in file_paths:
                path = Path(fp)
                if not path.exists():
                    continue

                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    file_content = f.read()

                clean_code = self.sanitizer.sanitize(file_content)
                code_tokens = self.estimate_tokens(clean_code)

                if code_tokens <= remaining_budget:
                    file_text = f"### File: {fp}\n```\n{clean_code}\n```"
                    tokens = code_tokens
                else:
                    # File exceeds budget -> generate hierarchical summary (FR15)
                    summary = self.summarizer.summarize(fp)
                    clean_summary = self.sanitizer.sanitize(summary)
                    file_text = f"### File Outline (Summary): {fp}\n{clean_summary}"
                    tokens = self.estimate_tokens(clean_summary)

                if remaining_budget - tokens < 50:
                    break

                file_section_lines.append(file_text)
                remaining_budget -= tokens
                included_files.append(fp)

            if len(file_section_lines) > 1:
                prompt_sections.append("\n".join(file_section_lines))

        # 5. Assemble final prompt string
        final_prompt_parts = [
            f"SYSTEM: {clean_system}\n",
            "\n\n".join(prompt_sections),
            f"\n\nUSER OBJECTIVE:\n{clean_query}"
        ]

        full_prompt = "\n".join([p for p in final_prompt_parts if p.strip()])
        total_tokens = self.estimate_tokens(full_prompt)

        return {
            "prompt": full_prompt,
            "token_count": total_tokens,
            "included_memories": included_memories,
            "included_files": included_files,
            "sanitized_query": clean_query,
        }

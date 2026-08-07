"""
Repo Intelligence & Tiered Memory Engine

This package provides repository analysis, tiered memory management,
and context assembly for the AE-01 Unified Agentic Coding Harness.

Primary surfaces:
- Repository Intelligence: AST parsing, symbol indexing, call graphs
- Tiered Memory: Working, Task, Project, Episodic, Procedural, Preference, Evidence
- Context Manager: Token-budgeted context assembly with relevance ranking and sanitization
"""

__version__ = "0.3.0"  # Phase 3 complete

# Database exports
from .db import (
    init_db,
    get_db_session,
    SessionModel,
    MemoryItemModel,
    SymbolIndexModel,
    CallGraphEdgeModel,
)

# Indexer exports
from .indexer import (
    scan_repository,
    FileScanner,
    ASTParser,
    parse_file,
    SymbolGraph,
    TestMapper,
    GitInspector,
    GitInspectorError,
)

# Memory exports
from .memory import (
    TieredMemoryStore,
    ProvenanceRecord,
    create_provenance_record,
    validate_provenance,
    MemoryInvalidator,
    invalidate_stale_memories,
    MemoryExporter,
    export_memory_tier,
    import_memory,
)

# Context exports
from .context import (
    ContextManager,
    RelevanceRanker,
    rank_context_items,
    FileSummarizer,
    summarize_file,
    Sanitizer,
    sanitize_prompt_text,
)

__all__ = [
    # Database
    "init_db",
    "get_db_session",
    "SessionModel",
    "MemoryItemModel",
    "SymbolIndexModel",
    "CallGraphEdgeModel",
    # Indexer
    "scan_repository",
    "FileScanner",
    "ASTParser",
    "parse_file",
    "SymbolGraph",
    "TestMapper",
    "GitInspector",
    "GitInspectorError",
    # Memory
    "TieredMemoryStore",
    "ProvenanceRecord",
    "create_provenance_record",
    "validate_provenance",
    "MemoryInvalidator",
    "invalidate_stale_memories",
    "MemoryExporter",
    "export_memory_tier",
    "import_memory",
    # Context
    "ContextManager",
    "RelevanceRanker",
    "rank_context_items",
    "FileSummarizer",
    "summarize_file",
    "Sanitizer",
    "sanitize_prompt_text",
]

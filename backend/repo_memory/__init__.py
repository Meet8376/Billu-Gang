"""
Repo Intelligence & Tiered Memory Engine

This package provides repository analysis, tiered memory management,
context assembly, memory ablations, and initialization tools for the AE-01 Unified Agentic Coding Harness.

Primary surfaces:
- Repository Intelligence: AST parsing, symbol indexing, call graphs, incremental indexer
- Tiered Memory: Working, Task, Project, Episodic, Procedural, Preference, Evidence, Memory Ablations
- Context Manager: Token-budgeted context assembly, relevance ranking, sanitization, latency profiler
- Database Init: Fresh database initialization script (`initialize_harness_repo_memory`)
"""

__version__ = "1.0.0"  # Complete 6-Phase Deliverable

# Database exports
from .db import (
    init_db,
    get_db_session,
    SessionModel,
    MemoryItemModel,
    SymbolIndexModel,
    CallGraphEdgeModel,
    initialize_harness_repo_memory,
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
    IncrementalIndexer,
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
    MemoryAblationController,
    MemoryAblationMode,
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
    ContextLatencyProfiler,
)

__all__ = [
    # Database
    "init_db",
    "get_db_session",
    "SessionModel",
    "MemoryItemModel",
    "SymbolIndexModel",
    "CallGraphEdgeModel",
    "initialize_harness_repo_memory",
    # Indexer
    "scan_repository",
    "FileScanner",
    "ASTParser",
    "parse_file",
    "SymbolGraph",
    "TestMapper",
    "GitInspector",
    "GitInspectorError",
    "IncrementalIndexer",
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
    "MemoryAblationController",
    "MemoryAblationMode",
    # Context
    "ContextManager",
    "RelevanceRanker",
    "rank_context_items",
    "FileSummarizer",
    "summarize_file",
    "Sanitizer",
    "sanitize_prompt_text",
    "ContextLatencyProfiler",
]

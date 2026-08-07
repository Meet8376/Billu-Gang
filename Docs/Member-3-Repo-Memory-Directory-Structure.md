# Member 3 — Repo Intelligence & Tiered Memory Lead: Directory Structure & File Specification

## 1. Overview & Ownership Domain
- **Member:** Member 3
- **Primary Role:** Repo Intelligence & Tiered Memory Lead
- **Engineering Surfaces Owned:** Repository Intelligence, Tiered Memory Engine, Context Manager
- **Tech Stack & Tools:** Tree-sitter (Python bindings), GitPython, ripgrep (via subprocess), SQLite (via SQLAlchemy), sentence-transformers, tiktoken, NetworkX
- **Primary Root Location:** `backend/repo_memory/`

---

## 2. Dedicated Directory Tree

```
backend/repo_memory/
├── __init__.py                         # Package initializer
│
├── db/                                 # Database Storage & Schema Layer (SQLite via SQLAlchemy)
│   ├── __init__.py
│   ├── database.py                     # SQLAlchemy engine creation, sessionmaker & DB initialization
│   ├── models.py                       # SQLAlchemy ORM Models (SessionModel, MemoryItemModel, SymbolIndexModel)
│   └── migrations/                     # Alembic migration scripts for database schema evolution
│
├── indexer/                            # Polyglot Repository Indexing Engine
│   ├── __init__.py
│   ├── ast_parser.py                   # Tree-sitter parser for Python, TypeScript & JavaScript AST extraction
│   ├── symbol_graph.py                 # Symbol indexer & polyglot call graph builder (NetworkX)
│   ├── git_inspector.py                # GitPython git blame, commit history & workspace diff inspector
│   ├── file_scanner.py                 # Directory scanner adhering strictly to .gitignore rules
│   └── test_mapper.py                  # Automatic test-to-source file association mapper (FR2)
│
├── memory/                             # Tiered Memory Engine & Provenance Management
│   ├── __init__.py
│   ├── tiered_store.py                 # TieredMemoryStore CRUD engine (Working, Task, Project, Episodic, etc.)
│   ├── provenance.py                   # Metadata provenance manager (source file, timestamp, model ID, confidence)
│   ├── invalidation.py                 # Automatic memory invalidation engine on file edits (FR11)
│   └── memory_exporter.py              # Serializer/deserializer to import, export, and clear memory tiers (FR12)
│
├── context/                            # Context Manager & Token Budget Optimizer
│   ├── __init__.py
│   ├── context_manager.py              # Dynamic token-budgeted prompt context assembler
│   ├── relevance_ranker.py             # Semantic relevance scoring via sentence-transformers / embeddings
│   ├── summarizer.py                   # Hierarchical file summarization for oversized files (FR15)
│   └── sanitizer.py                    # Prompt-injection & credential sanitizer for external code/issues (FR17)
│
└── tests/                              # Unit & Integration Tests for Repo & Memory
    ├── __init__.py
    ├── test_ast_parser.py              # Tree-sitter symbol parsing tests across languages
    ├── test_symbol_graph.py            # NetworkX call graph traversal & symbol resolution tests
    ├── test_tiered_store.py            # SQLite CRUD & provenance enforcement tests
    ├── test_invalidation.py            # Memory auto-invalidation on file mutation tests
    └── test_context_manager.py         # Token budget ranking & prompt assembly tests
```

---

## 3. Detailed File Responsibilities & Key Exports

| File Path | Purpose & Responsibilities | Key Functions / Classes / Components |
|---|---|---|
| `backend/repo_memory/db/database.py` | Initializes SQLite connection (`sqlite:///harness.db`), session manager. | `get_db_session()`, `init_db()` |
| `backend/repo_memory/db/models.py` | ORM tables: `sessions`, `memory_items`, `symbol_index`, `call_graph`. | `MemoryItemModel`, `SymbolIndexModel` |
| `backend/repo_memory/indexer/ast_parser.py` | Uses `tree-sitter` to parse ASTs, extract function definitions, classes, and imports. | `class ASTParser`, `parse_file(path)` |
| `backend/repo_memory/indexer/symbol_graph.py` | Builds directed import/call graph using NetworkX to identify structural dependencies. | `class SymbolGraph`, `get_callers()` |
| `backend/repo_memory/indexer/git_inspector.py` | Wraps GitPython to query git log, git blame, commit authors, and working tree changes. | `class GitInspector`, `get_file_blame()` |
| `backend/repo_memory/indexer/file_scanner.py` | Scans workspace directory while ignoring files listed in `.gitignore` or default exclusions. | `scan_repository(repo_path)` |
| `backend/repo_memory/indexer/test_mapper.py` | Maps test files (e.g., `test_auth.py`) to implementation files (`auth.py`). | `find_related_tests(source_file)` |
| `backend/repo_memory/memory/tiered_store.py` | Core CRUD operations for memory items across 7 tiers (working, task, project, etc.). | `class TieredMemoryStore` (`add()`, `query()`) |
| `backend/repo_memory/memory/provenance.py` | Attaches metadata (source file line, timestamp, author model, confidence score) to memories. | `create_provenance_record()` |
| `backend/repo_memory/memory/invalidation.py` | Automatically flags or purges memory items when target files are updated. | `invalidate_stale_memories(modified_files)` |
| `backend/repo_memory/memory/memory_exporter.py` | Exports memory store to JSON/YAML or re-hydrates store during benchmark replays. | `export_memory_tier()`, `import_memory()` |
| `backend/repo_memory/context/context_manager.py` | Dynamically ranks and selects top relevant symbols/memories to fit exact LLM token budget. | `class ContextManager`, `assemble_context()` |
| `backend/repo_memory/context/relevance_ranker.py` | Computes cosine similarity embeddings using `sentence-transformers` for RAG lookup. | `rank_relevance(query, items)` |
| `backend/repo_memory/context/summarizer.py` | Generates concise outline summaries for large files exceeding context limits. | `summarize_file(path, max_tokens)` |
| `backend/repo_memory/context/sanitizer.py` | Strips potential prompt-injections, secret keys, and passwords from ingested issues. | `sanitize_prompt_text(text)` |

---

## 4. 24-Hour Phase Deliverables Schedule

```
Phase 1 (H0-H3) ──► Phase 2 (H3-H8) ──► Phase 3 (H8-H13) ──► Phase 4 (H13-H17) ──► Phase 5 (H17-H21) ──► Phase 6 (H21-H24)
  SQLite Schema &     AST Symbol Graph &   Context Ranking &     Memory Provenance &   Memory Ablations &    Clean Init Script
  Tree-sitter Setup   Tiered Memory CRUD   Auto-Invalidation     Incremental Re-Index   Latency Profiling     (`harness init`)
```

1. **Phase 1 (Hours 0–3):**
   - Set up SQLite database schema via SQLAlchemy for Tiered Memory and Repo Index (`db/database.py`, `db/models.py`).
   - Create polyglot AST parser using `tree-sitter` for Python/TypeScript symbol extraction (`indexer/ast_parser.py`).
   - Implement `file_scanner.py` with `.gitignore` exclusion logic.
2. **Phase 2 (Hours 3–8):**
   - Build symbol graph and call graph engine using NetworkX (`indexer/symbol_graph.py`).
   - Implement test-to-source file mapping logic (`indexer/test_mapper.py`).
   - Build `TieredMemoryStore` CRUD methods supporting 7 memory tiers (`memory/tiered_store.py`).
3. **Phase 3 (Hours 8–13):**
   - Integrate `ContextManager` into model prompt pipeline: budget context window and rank symbols by relevance.
   - Implement automatic memory invalidation when target files are updated inside sandbox (`memory/invalidation.py`).
   - Add prompt-injection & secret sanitization (`context/sanitizer.py`).
4. **Phase 4 (Hours 13–17):**
   - Add metadata provenance tracking (source file, timestamp, model ID, confidence) to all `MemoryItem` records.
   - Build incremental repo index refresher triggered after every sandbox code edit.
   - Implement hierarchical file summarization for files exceeding token context budget.
5. **Phase 5 (Hours 17–21):**
   - Verify memory ablation flags: memory ON vs. memory OFF (cold vs. warm memory retrieval).
   - Benchmark index retrieval latency ensuring context assembly stays under 20% total wall-clock time.
6. **Phase 6 (Hours 21–24):**
   - Verify clean database initialization script for fresh user onboarding (`harness init`).

---

## 5. Subsystem Dependencies & API Boundaries
- **Repo & Memory ↔ Database:** Manages local `harness.db` SQLite database file.
- **Repo & Memory ↔ Model Adapter:** Provides token-budgeted context block (`assemble_context()`) to `ModelAdapter`.
- **Repo & Memory ↔ Sandbox:** Receives file change notifications from sandbox to trigger memory invalidation and incremental re-indexing.

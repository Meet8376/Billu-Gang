# AE-01 Backend - Repo Intelligence & Tiered Memory

Backend implementation for the Unified Agentic Coding Harness.

## Member 3: Repo Intelligence & Tiered Memory Lead

This module provides:
- **Repository Intelligence**: AST parsing, symbol indexing, call graphs
- **Tiered Memory Engine**: 7-tier memory system with provenance
- **Context Manager**: Token-budgeted context assembly

## Installation

```bash
cd backend
pip install -r requirementsm3.txt
```

## Structure

```
backend/repo_memory/
├── db/                    # Database layer (SQLite + SQLAlchemy)
├── indexer/               # Repository indexing
├── memory/                # Tiered memory engine
├── context/               # Context manager
└── tests/                 # Test suite
```

## Phase 1 Deliverables (Hours 0-3) ✅

- [x] SQLite database schema via SQLAlchemy
- [x] Polyglot AST parser using tree-sitter (with regex fallback)
- [x] File scanner with .gitignore exclusion logic
- [x] Comprehensive test suite

## Running Tests

```bash
# Run all tests
pytest backend/repo_memory/tests/

# Run specific test file
pytest backend/repo_memory/tests/test_database.py

# Run with coverage
pytest --cov=backend.repo_memory backend/repo_memory/tests/
```

## Quick Start

```python
from backend.repo_memory.db import init_db, get_db_session, SessionModel
from backend.repo_memory.indexer import scan_repository, parse_file

# Initialize database
init_db()

# Scan repository
files = scan_repository("/path/to/repo")
print(f"Found {len(files)} files")

# Parse a file
symbols = parse_file("example.py")
for symbol in symbols:
    print(f"{symbol.symbol_type}: {symbol.name} at line {symbol.start_line}")

# Create a session
with get_db_session() as session:
    repo_session = SessionModel(repo_path="/path/to/repo")
    session.add(repo_session)
    session.commit()
```

## Next Steps (Phase 2)

- [ ] Build symbol graph and call graph engine using NetworkX
- [ ] Implement test-to-source file mapping
- [ ] Build TieredMemoryStore CRUD methods

## Tech Stack

- **Database**: SQLite via SQLAlchemy
- **AST Parsing**: tree-sitter (Python bindings)
- **Testing**: pytest
- **Languages Supported**: Python, TypeScript, JavaScript

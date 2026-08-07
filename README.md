# Billu-Gang - AE-01 Unified Agentic Coding Harness

A model-independent, terminal-based coding harness that autonomously handles software engineering tasks from issue intake to verified patch delivery.

## Project Overview

Modern coding agents compete on model quality alone, obscuring how much performance comes from the **harness** — context construction, memory, orchestration, tooling, and verification. This project builds a harness that proves its value independent of the underlying model.

## Architecture

The system is built around seven first-class engineering surfaces:
1. **Model Adapter Layer** - Model-independent LLM interface
2. **Repository Intelligence** - AST parsing, symbol indexing, call graphs
3. **Tiered Memory** - 7-tier memory system with provenance
4. **Context Manager** - Token-budgeted context assembly
5. **Task Graph/Planner** - Multi-agent orchestration
6. **Sandboxed Execution** - Safe, isolated command execution
7. **Verification-First Completion** - Build/test/lint-based completion

## Team Structure

- **Member 1**: Terminal CLI (Node.js/TypeScript)
- **Member 2**: Backend Core & Model Adapter (Python/FastAPI)
- **Member 3**: Repo Intelligence & Tiered Memory (Python) ✅
- **Member 4**: Task Orchestrator & Sandbox (Python)
- **Member 5**: Verification & Benchmark Pipeline (Python)

## Member 3 Progress: Repo Intelligence & Tiered Memory

### Phase 1 Complete ✅ (Hours 0-3)

- [x] SQLite database schema with SQLAlchemy
- [x] Tiered memory models (7 tiers: Working, Task, Project, Episodic, Procedural, Preference, Evidence)
- [x] Symbol index models with provenance tracking
- [x] Call graph edge models
- [x] Polyglot AST parser (Python, TypeScript, JavaScript)
- [x] File scanner with .gitignore support
- [x] Comprehensive test suite
- [x] Demo script

### Quick Start (Member 3)

```bash
# Install dependencies
cd backend
pip install -r requirementsm3.txt

# Run tests
pytest repo_memory/tests/

# Run Phase 1 demo
python demo_phase1.py
```

### Directory Structure

```
backend/repo_memory/
├── db/                    # Database layer
│   ├── database.py       # SQLAlchemy engine & session management
│   ├── models.py         # ORM models (Session, Memory, Symbol, CallGraph)
│   └── migrations/       # Alembic migrations (future)
├── indexer/              # Repository indexing
│   ├── ast_parser.py     # Tree-sitter AST parsing
│   ├── symbol_graph.py   # Symbol & call graph builder (Phase 2)
│   ├── git_inspector.py  # Git history inspection (Phase 2)
│   ├── file_scanner.py   # .gitignore-aware file scanner
│   └── test_mapper.py    # Test-to-source mapping (Phase 2)
├── memory/               # Tiered memory engine (Phase 2)
├── context/              # Context manager (Phase 3)
└── tests/                # Test suite
```

## Documentation

See `Docs/` for detailed specifications:
- `PRD.md` - Product Requirements
- `Architecture.md` - System Architecture
- `Tech-Stack.md` - Technology Stack
- `Member-3-Repo-Memory-Directory-Structure.md` - Member 3 Spec

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Frontend**: Node.js, TypeScript, Ink (terminal UI)
- **Database**: SQLite
- **Parsing**: tree-sitter
- **Testing**: pytest

## Development Status

🚧 **Active Development** - Phase 1 Complete

Next up: Phase 2 (Symbol Graph & Tiered Memory CRUD)
#!/usr/bin/env python3
"""
Phase 1 Demo Script

Demonstrates:
1. Database initialization
2. Repository scanning
3. AST parsing and symbol extraction
4. Memory item creation with provenance
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.repo_memory.db import (
    init_db,
    get_db_session,
    SessionModel,
    MemoryItemModel,
    SymbolIndexModel,
)
from backend.repo_memory.db.models import MemoryTier
from backend.repo_memory.indexer import scan_repository, parse_file


def main():
    print("=" * 60)
    print("AE-01 Repo Intelligence & Tiered Memory - Phase 1 Demo")
    print("=" * 60)
    print()
    
    # 1. Initialize database
    print("📊 Initializing database...")
    db_path = "demo_harness.db"
    init_db(db_path, force_recreate=True)
    print(f"✅ Database initialized: {db_path}")
    print()
    
    # 2. Scan this repository
    print("🔍 Scanning repository...")
    repo_path = str(Path(__file__).parent.parent)
    files = scan_repository(repo_path, include_extensions={".py", ".md"})
    print(f"✅ Found {len(files)} files")
    print(f"   Sample files: {files[:5]}")
    print()
    
    # 3. Parse Python files
    print("🌳 Parsing Python files...")
    all_symbols = []
    python_files = [f for f in files if f.endswith(".py")][:3]  # Parse first 3
    
    for file_path in python_files:
        full_path = Path(repo_path) / file_path
        if full_path.exists():
            try:
                symbols = parse_file(str(full_path))
                all_symbols.extend(symbols)
                print(f"   📄 {file_path}: {len(symbols)} symbols")
            except Exception as e:
                print(f"   ⚠️  {file_path}: {e}")
    
    print(f"✅ Total symbols extracted: {len(all_symbols)}")
    print()
    
    # 4. Store in database
    print("💾 Storing data in database...")
    with get_db_session(db_path) as session:
        # Create session
        repo_session = SessionModel(
            repo_path=repo_path,
            model_provider="demo",
        )
        session.add(repo_session)
        session.flush()
        
        # Store symbols
        for symbol in all_symbols[:10]:  # Store first 10
            symbol_entry = SymbolIndexModel(
                session_id=repo_session.id,
                file_path=symbol.file_path,
                symbol_name=symbol.name,
                symbol_type=symbol.symbol_type,
                language=symbol.language,
                start_line=symbol.start_line,
                end_line=symbol.end_line,
                signature=symbol.signature,
                parent_symbol=symbol.parent_symbol,
            )
            session.add(symbol_entry)
        
        # Create memory items for each tier
        for tier in MemoryTier:
            memory = MemoryItemModel(
                session_id=repo_session.id,
                tier=tier.value,
                content=f"Demo memory item for {tier.value} tier",
                source_file=python_files[0] if python_files else None,
                confidence=0.95,
                invalidation_rule={"type": "demo"},
            )
            session.add(memory)
        
        session.commit()
        
        # Query back
        symbol_count = session.query(SymbolIndexModel).count()
        memory_count = session.query(MemoryItemModel).count()
        
        print(f"✅ Stored {symbol_count} symbols")
        print(f"✅ Stored {memory_count} memory items")
        print()
    
    # 5. Display some results
    print("📋 Sample Results:")
    print("-" * 60)
    
    with get_db_session(db_path) as session:
        # Show some symbols
        symbols = session.query(SymbolIndexModel).limit(5).all()
        print("\n🔤 Symbols:")
        for sym in symbols:
            parent_info = f" (in {sym.parent_symbol})" if sym.parent_symbol else ""
            print(f"   • {sym.symbol_type}: {sym.symbol_name}{parent_info}")
            print(f"     📍 {sym.file_path}:{sym.start_line}")
        
        # Show memory tiers
        memories = session.query(MemoryItemModel).all()
        print("\n🧠 Memory Tiers:")
        for mem in memories:
            print(f"   • {mem.tier}: {mem.content[:50]}...")
            print(f"     Confidence: {mem.confidence}, Valid: {bool(mem.is_valid)}")
    
    print()
    print("=" * 60)
    print("✅ Phase 1 Demo Complete!")
    print(f"📊 Database saved to: {db_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()

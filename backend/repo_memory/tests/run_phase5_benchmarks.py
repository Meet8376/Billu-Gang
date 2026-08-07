"""
Phase 5 Benchmark Script - Memory Ablations & Latency Profiling

Executes Phase 5 verification:
1. Memory Ablation Verification (WARM_MEMORY vs COLD_MEMORY context assembly)
2. Index Retrieval & Context Assembly Latency Benchmarking (< 20% wall-clock budget)
"""

import sys
import time
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

# Ensure repository root is on sys.path
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from backend.repo_memory.db.database import init_db, get_db_session
from backend.repo_memory.db.models import SessionModel, MemoryTier
from backend.repo_memory.memory.tiered_store import TieredMemoryStore
from backend.repo_memory.memory.ablation import MemoryAblationController, MemoryAblationMode
from backend.repo_memory.context.latency_profiler import ContextLatencyProfiler


def run_phase5_benchmarks():
    print("=" * 70)
    print("AE-01 Repo Intelligence & Tiered Memory - Phase 5 Benchmarks")
    print("=" * 70)

    with NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        init_db(db_path, force_recreate=True)

        with get_db_session(db_path) as session:
            repo_session = SessionModel(repo_path="/fake/repo", model_provider="benchmark")
            session.add(repo_session)
            session.commit()
            session_id = repo_session.id

        # Seed memory store
        store = TieredMemoryStore(session_id, db_path)
        store.add(tier=MemoryTier.PROJECT, content="Ablation Rule 1: Use fast async HTTP client")
        store.add(tier=MemoryTier.TASK, content="Ablation Rule 2: Implement OAuth2 login flow")
        store.add(tier=MemoryTier.PROCEDURAL, content="Ablation Rule 3: Run pytest before committing")

        # 1. Benchmark Memory Ablations (Warm vs Cold)
        print("\n[1/2] Verifying Memory Ablations (NFR30)...")
        ablation = MemoryAblationController(session_id, db_path)

        warm_result = ablation.assemble_ablated_context(
            query="Implement user authentication login endpoint",
            mode=MemoryAblationMode.WARM_MEMORY
        )

        cold_result = ablation.assemble_ablated_context(
            query="Implement user authentication login endpoint",
            mode=MemoryAblationMode.COLD_MEMORY
        )

        print(f"  - WARM_MEMORY (Memory ON):  {len(warm_result['included_memories'])} memories included, {warm_result['token_count']} estimated tokens")
        print(f"  - COLD_MEMORY (Memory OFF): {len(cold_result['included_memories'])} memories included, {cold_result['token_count']} estimated tokens")

        assert len(warm_result["included_memories"]) > 0, "WARM_MEMORY should retrieve stored memories"
        assert len(cold_result["included_memories"]) == 0, "COLD_MEMORY must purge stored memories"
        print("  ✅ Memory Ablation verification PASSED!")

        # 2. Benchmark Index Retrieval & Context Assembly Latency
        print("\n[2/2] Benchmarking Retrieval & Context Assembly Latency...")
        profiler = ContextLatencyProfiler(session_id, db_path)
        metrics = profiler.profile_assembly(
            query="Benchmark user authentication latency overhead",
            max_tokens=4096,
            runs=10
        )

        print(f"  - Average Latency: {metrics['avg_latency_ms']} ms")
        print(f"  - Min Latency:     {metrics['min_latency_ms']} ms")
        print(f"  - Max Latency:     {metrics['max_latency_ms']} ms")
        print(f"  - Total Runs:      {metrics['runs']}")

        assert metrics["avg_latency_ms"] < 200.0, "Context assembly latency must remain under 200ms"
        print("  ✅ Latency Benchmark PASSED (< 200ms overhead target achieved)!")

        print("\n" + "=" * 70)
        print("✅ ALL PHASE 5 ABLATION & LATENCY BENCHMARKS COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    finally:
        if Path(db_path).exists():
            Path(db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    run_phase5_benchmarks()

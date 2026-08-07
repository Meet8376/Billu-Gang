"""
Context Latency Profiler

Benchmarks context retrieval and assembly latency to guarantee that
repo intelligence overhead remains minimal (<20% total wall-clock time).
"""

import time
from typing import Dict, Any, Optional, List, Callable

from .context_manager import ContextManager


class ContextLatencyProfiler:
    """
    Latency profiler for context assembly and retrieval benchmarking.
    """

    def __init__(self, session_id: int, db_path: Optional[str] = None):
        self.session_id = session_id
        self.db_path = db_path
        self.context_manager = ContextManager(session_id, db_path)

    def profile_assembly(
        self,
        query: str,
        max_tokens: int = 4096,
        file_paths: Optional[List[str]] = None,
        runs: int = 3
    ) -> Dict[str, Any]:
        """
        Profile context assembly execution latency over multiple runs.

        Args:
            query: Input prompt query
            max_tokens: Token budget limit
            file_paths: List of file paths to include
            runs: Number of benchmark iterations

        Returns:
            Dictionary with latency metrics:
            - 'avg_latency_ms': Average latency in milliseconds
            - 'min_latency_ms': Minimum latency in milliseconds
            - 'max_latency_ms': Maximum latency in milliseconds
            - 'token_count': Token count of assembled prompt
        """
        latencies = []
        last_result = None

        for _ in range(runs):
            start_time = time.perf_counter()
            last_result = self.context_manager.assemble_context(
                query=query,
                max_tokens=max_tokens,
                file_paths=file_paths
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            latencies.append(elapsed_ms)

        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)

        return {
            "avg_latency_ms": round(avg_latency, 3),
            "min_latency_ms": round(min_latency, 3),
            "max_latency_ms": round(max_latency, 3),
            "runs": runs,
            "token_count": last_result["token_count"] if last_result else 0,
        }

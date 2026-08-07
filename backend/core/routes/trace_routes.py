"""
Trace, Model Independence Benchmark & Financial Report Route Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.core.schemas.session import FinancialSummaryReport, ModelBenchmarkMetrics
from backend.core.adapters import LangChainAdapter, MockAdapter
from backend.core.tracking import CostTracker

router = APIRouter()

# Global cost tracker instance for report serving stub
_global_cost_tracker = CostTracker(max_budget_usd=10.0)


class BenchmarkRequest(BaseModel):
    session_id: str
    models_to_verify: List[str] = ["gpt-4o", "mock-model"]


class TraceLogEntry(BaseModel):
    session_id: str
    timestamp: str
    log_level: str
    message: str


@router.get("/trace/{session_id}", response_model=List[TraceLogEntry])
async def get_trace_log(session_id: str):
    """Retrieve event trace logs for a session."""
    return []


@router.post("/benchmark/model-swap", response_model=List[ModelBenchmarkMetrics])
async def execute_model_swap_verification(payload: BenchmarkRequest):
    """Execute model independence verification: run benchmarks across model adapters with zero harness changes."""
    results: List[ModelBenchmarkMetrics] = []

    for model_name in payload.models_to_verify:
        start_time = time.time()

        if model_name == "mock-model":
            adapter = MockAdapter(model_name="mock-model")
        else:
            adapter = LangChainAdapter(model_name=model_name)

        resp = await adapter.complete(
            messages=[{"role": "user", "content": "Execute model independence verification test"}]
        )
        latency = round(time.time() - start_time, 3)

        cost = _global_cost_tracker.add_usage(
            model=model_name,
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
            latency_seconds=latency
        )

        metric = ModelBenchmarkMetrics(
            model_name=model_name,
            tokens_input=resp.input_tokens,
            tokens_output=resp.output_tokens,
            total_tokens=resp.total_tokens,
            wall_clock_latency_seconds=latency,
            cost_usd=cost,
            success=True,
            harness_modified=False,
        )
        _global_cost_tracker.record_benchmark(metric)
        results.append(metric)

    return results


@router.get("/cost/report/{session_id}", response_model=FinancialSummaryReport)
async def get_financial_summary_report(session_id: str):
    """Generate total token usage, wall-clock latency, and financial USD cost report."""
    return _global_cost_tracker.generate_financial_summary_report(session_id=session_id)

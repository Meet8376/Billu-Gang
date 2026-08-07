"""
Trace, Security Sanitized Logs, Model Independence Benchmark & Financial Report Route Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.core.schemas.session import FinancialSummaryReport, ModelBenchmarkMetrics
from backend.core.adapters import LangChainAdapter, MockAdapter
from backend.core.tracking import CostTracker
from backend.core.security import CredentialSanitizer

router = APIRouter()

# Global cost tracker instance for report serving stub
_global_cost_tracker = CostTracker(max_budget_usd=10.0)

# Global trace log store
_trace_store: List["TraceLogEntry"] = []


class BenchmarkRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier for benchmark run")
    models_to_verify: List[str] = Field(
        default=["gpt-4o", "mock-model"],
        description="List of model adapter names to evaluate for model swap verification",
    )


class TraceLogEntry(BaseModel):
    session_id: str = Field(..., description="Session ID linked to trace entry")
    timestamp: str = Field(..., description="ISO timestamp of event")
    log_level: str = Field("INFO", description="Log level (INFO, WARN, ERROR)")
    message: str = Field(..., description="Trace event message (auto-sanitized for security)")


@router.get(
    "/trace/{session_id}",
    response_model=List[TraceLogEntry],
    summary="Retrieve Session Trace Logs",
    description="Fetch security-sanitized event trace logs for an active session.",
)
async def get_trace_log(session_id: str) -> List[TraceLogEntry]:
    """Retrieve sanitized trace logs for a session."""
    session_traces = [t for t in _trace_store if t.session_id == session_id]
    # Extra safety pass to ensure no secrets in returned list
    sanitized_traces = []
    for entry in session_traces:
        clean_msg, _ = CredentialSanitizer.sanitize_text(entry.message)
        sanitized_traces.append(
            TraceLogEntry(
                session_id=entry.session_id,
                timestamp=entry.timestamp,
                log_level=entry.log_level,
                message=clean_msg,
            )
        )
    return sanitized_traces


@router.post(
    "/trace",
    response_model=TraceLogEntry,
    status_code=status.HTTP_201_CREATED,
    summary="Post Trace Event Log",
    description="Ingest a new trace log entry. Automatically redacts API keys or credentials before saving to trace store.",
)
async def create_trace_log(entry: TraceLogEntry) -> TraceLogEntry:
    """Add a trace event log entry, automatically sanitizing sensitive tokens."""
    clean_msg, _ = CredentialSanitizer.sanitize_text(entry.message)
    sanitized_entry = TraceLogEntry(
        session_id=entry.session_id,
        timestamp=entry.timestamp,
        log_level=entry.log_level,
        message=clean_msg,
    )
    _trace_store.append(sanitized_entry)
    return sanitized_entry


@router.post(
    "/benchmark/model-swap",
    response_model=List[ModelBenchmarkMetrics],
    summary="Execute Model Swap Verification",
    description="Execute model independence verification benchmark suite: switch model adapters with zero harness code changes and record performance.",
)
async def execute_model_swap_verification(payload: BenchmarkRequest) -> List[ModelBenchmarkMetrics]:
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
            latency_seconds=latency,
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


@router.get(
    "/cost/report/{session_id}",
    response_model=FinancialSummaryReport,
    summary="Generate Financial Summary Report",
    description="Generate total token usage, wall-clock latency, and financial USD cost report for a session.",
)
async def get_financial_summary_report(session_id: str) -> FinancialSummaryReport:
    """Generate total token usage, wall-clock latency, and financial USD cost report."""
    return _global_cost_tracker.generate_financial_summary_report(session_id=session_id)

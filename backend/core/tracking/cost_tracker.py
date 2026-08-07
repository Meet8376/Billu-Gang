"""
Real-time USD Cost Accumulator Engine ($/1k tokens per model) & Financial Report Generator.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

from backend.core.schemas.session import FinancialSummaryReport, ModelBenchmarkMetrics


# Pricing table per 1,000 tokens (USD)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"input": 0.0025, "output": 0.010},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-5-haiku-20241022": {"input": 0.0008, "output": 0.004},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    "gemini-pro": {"input": 0.0005, "output": 0.0015},
    "mock-model": {"input": 0.0, "output": 0.0},
    "default": {"input": 0.0025, "output": 0.010},
}


class UsageRecord(BaseModel):
    """Individual invocation usage log record with latency."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_seconds: float = 0.0


class CostTracker:
    """Calculates and accumulates session token usage, latency, and financial cost."""

    def __init__(self, max_budget_usd: float = 10.0, warning_threshold: float = 0.8):
        self.max_budget_usd = max_budget_usd
        self.warning_threshold = warning_threshold
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.total_latency_seconds: float = 0.0
        self.records: List[UsageRecord] = []
        self.benchmark_metrics: List[ModelBenchmarkMetrics] = []

    def add_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_seconds: float = 0.0
    ) -> float:
        """Accumulate token counts and return incremental USD cost."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        input_cost = (input_tokens / 1000.0) * pricing["input"]
        output_cost = (output_tokens / 1000.0) * pricing["output"]
        incremental_cost = input_cost + output_cost

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += incremental_cost
        self.total_latency_seconds += latency_seconds

        self.records.append(
            UsageRecord(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=incremental_cost,
                latency_seconds=latency_seconds,
            )
        )

        return incremental_cost

    def record_benchmark(self, metrics: ModelBenchmarkMetrics):
        """Record model independence benchmark run metrics."""
        self.benchmark_metrics.append(metrics)

    def is_budget_exceeded(self) -> bool:
        """Check whether accumulated USD cost exceeds maximum session budget."""
        return self.total_cost_usd >= self.max_budget_usd

    def is_warning_threshold_reached(self) -> bool:
        """Check whether cost reached warning percentage."""
        return self.total_cost_usd >= (self.max_budget_usd * self.warning_threshold)

    def generate_financial_summary_report(self, session_id: str) -> FinancialSummaryReport:
        """Generate comprehensive financial cost, token usage, and latency summary report."""
        per_model: Dict[str, Dict[str, Any]] = {}
        for r in self.records:
            if r.model not in per_model:
                per_model[r.model] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost_usd": 0.0,
                    "latency_seconds": 0.0,
                    "calls": 0,
                }
            per_model[r.model]["input_tokens"] += r.input_tokens
            per_model[r.model]["output_tokens"] += r.output_tokens
            per_model[r.model]["total_tokens"] += (r.input_tokens + r.output_tokens)
            per_model[r.model]["cost_usd"] = round(per_model[r.model]["cost_usd"] + r.cost_usd, 6)
            per_model[r.model]["latency_seconds"] = round(per_model[r.model]["latency_seconds"] + r.latency_seconds, 3)
            per_model[r.model]["calls"] += 1

        return FinancialSummaryReport(
            session_id=session_id,
            total_input_tokens=self.total_input_tokens,
            total_output_tokens=self.total_output_tokens,
            total_tokens=self.total_input_tokens + self.total_output_tokens,
            total_cost_usd=round(self.total_cost_usd, 6),
            total_latency_seconds=round(self.total_latency_seconds, 3),
            max_budget_usd=self.max_budget_usd,
            budget_exceeded=self.is_budget_exceeded(),
            per_model_breakdown=per_model,
            benchmark_models_verified=self.benchmark_metrics,
        )

    def get_summary(self) -> Dict[str, Any]:
        """Return structured summary dictionary."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "total_latency_seconds": round(self.total_latency_seconds, 3),
            "max_budget_usd": self.max_budget_usd,
            "budget_exceeded": self.is_budget_exceeded(),
            "records_count": len(self.records),
        }

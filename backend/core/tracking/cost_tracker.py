"""
Real-time USD Cost Accumulator Engine ($/1k tokens per model).
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import Dict, List
from datetime import datetime
from pydantic import BaseModel, Field


# Pricing table per 1,000 tokens (USD)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"input": 0.0025, "output": 0.010},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-5-haiku-20241022": {"input": 0.0008, "output": 0.004},
    "mock-model": {"input": 0.0, "output": 0.0},
    "default": {"input": 0.0025, "output": 0.010},
}


class UsageRecord(BaseModel):
    """Individual invocation usage log record."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


class CostTracker:
    """Calculates and accumulates session token usage and financial cost."""

    def __init__(self, max_budget_usd: float = 10.0, warning_threshold: float = 0.8):
        self.max_budget_usd = max_budget_usd
        self.warning_threshold = warning_threshold  # 80% default warning
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.records: List[UsageRecord] = []

    def add_usage(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Accumulate token counts and return incremental USD cost."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        input_cost = (input_tokens / 1000.0) * pricing["input"]
        output_cost = (output_tokens / 1000.0) * pricing["output"]
        incremental_cost = input_cost + output_cost

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += incremental_cost

        self.records.append(
            UsageRecord(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=incremental_cost
            )
        )

        return incremental_cost

    def is_budget_exceeded(self) -> bool:
        """Check whether accumulated USD cost exceeds maximum session budget."""
        return self.total_cost_usd >= self.max_budget_usd

    def is_warning_threshold_reached(self) -> bool:
        """Check whether cost reached warning percentage (e.g. 80%)."""
        return self.total_cost_usd >= (self.max_budget_usd * self.warning_threshold)

    def get_summary(self) -> Dict[str, Any]:
        """Return structured summary of usage and financial metrics."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "max_budget_usd": self.max_budget_usd,
            "budget_exceeded": self.is_budget_exceeded(),
            "records_count": len(self.records),
        }

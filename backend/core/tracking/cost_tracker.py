"""
Real-time USD Cost Accumulator Engine ($/1k tokens per model).
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import Dict


# Pricing table per 1,000 tokens (USD)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"input": 0.0025, "output": 0.010},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "mock-model": {"input": 0.0, "output": 0.0},
    "default": {"input": 0.0025, "output": 0.010},
}


class CostTracker:
    """Calculates and accumulates session token usage and financial cost."""

    def __init__(self, max_budget_usd: float = 10.0):
        self.max_budget_usd = max_budget_usd
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_cost_usd: float = 0.0

    def add_usage(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Accumulate token counts and return incremental USD cost."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        input_cost = (input_tokens / 1000.0) * pricing["input"]
        output_cost = (output_tokens / 1000.0) * pricing["output"]
        incremental_cost = input_cost + output_cost

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += incremental_cost

        return incremental_cost

    def is_budget_exceeded(self) -> bool:
        """Check whether accumulated USD cost exceeds maximum session budget."""
        return self.total_cost_usd >= self.max_budget_usd

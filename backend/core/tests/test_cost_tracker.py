"""
Phase 2 Unit Tests for Token & Cost Attribution Engine.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.tracking import count_tokens, count_tokens_for_messages, CostTracker


def test_count_tokens_text():
    text = "FastAPI backend core system tracking tokens."
    tokens = count_tokens(text, model="gpt-4o")
    assert tokens > 0


def test_count_tokens_messages():
    messages = [
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Write unit tests for cost tracker."},
    ]
    tokens = count_tokens_for_messages(messages, model="gpt-4o")
    assert tokens > 10


def test_cost_tracker_accumulation_and_warning():
    tracker = CostTracker(max_budget_usd=0.10, warning_threshold=0.8)

    # Add usage: gpt-4o input: $0.0025/1k, output: $0.010/1k
    cost1 = tracker.add_usage(model="gpt-4o", input_tokens=10000, output_tokens=5000)
    # cost1 = 10 * 0.0025 + 5 * 0.010 = 0.025 + 0.050 = 0.075 USD
    assert cost1 == pytest.approx(0.075, rel=1e-3)
    assert not tracker.is_budget_exceeded()

    # Second call reaching warning threshold ($0.080)
    cost2 = tracker.add_usage(model="gpt-4o", input_tokens=2000, output_tokens=1000)
    # total cost = 0.075 + 0.015 = 0.090 USD
    assert tracker.is_warning_threshold_reached()
    assert not tracker.is_budget_exceeded()

    # Third call exceeding budget ($0.10)
    tracker.add_usage(model="gpt-4o", input_tokens=5000, output_tokens=5000)
    assert tracker.is_budget_exceeded()

    summary = tracker.get_summary()
    assert summary["budget_exceeded"] is True
    assert summary["records_count"] == 3

"""
Unit Tests for Token & Cost Attribution.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.tracking import count_tokens, CostTracker


def test_count_tokens():
    text = "Hello world! This is a test string for token calculation."
    tokens = count_tokens(text)
    assert tokens > 0


def test_cost_tracker():
    tracker = CostTracker(max_budget_usd=1.0)
    cost = tracker.add_usage(model="gpt-4o", input_tokens=1000, output_tokens=1000)
    assert cost == pytest.approx(0.0125, rel=1e-3)
    assert tracker.total_cost_usd == pytest.approx(0.0125, rel=1e-3)
    assert not tracker.is_budget_exceeded()

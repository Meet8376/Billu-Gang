"""
Unit tests for RelevanceRanker (context/relevance_ranker.py)
"""

import pytest
from backend.repo_memory.context.relevance_ranker import RelevanceRanker, rank_context_items


def test_relevance_ranker_keyword_fallback():
    ranker = RelevanceRanker()
    
    items = [
        {"id": 1, "content": "Database user authentication and password hashing"},
        {"id": 2, "content": "Frontend UI component for dark mode toggle"},
        {"id": 3, "content": "User login session token management"},
    ]
    
    query = "user authentication login"
    ranked = ranker.rank_items(query, items, text_key="content")
    
    assert len(ranked) == 3
    assert "relevance_score" in ranked[0]
    # Item 1 or 3 should be highest ranked for user authentication query
    top_ids = [ranked[0]["id"], ranked[1]["id"]]
    assert 1 in top_ids or 3 in top_ids


def test_rank_context_items_convenience():
    items = [
        {"content": "Fix database connection leak"},
        {"content": "Update CSS colors"},
    ]
    ranked = rank_context_items("database connection", items)
    assert len(ranked) == 2
    assert ranked[0]["content"] == "Fix database connection leak"

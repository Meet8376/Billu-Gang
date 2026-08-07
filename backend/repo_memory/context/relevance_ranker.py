"""
Relevance Ranker

Ranks candidate memories, symbols, and code snippets by semantic relevance
to a target user query or coding task. Supports sentence-transformers embeddings
and keyword overlap fallbacks.
"""

import math
from typing import List, Dict, Any, Optional, Tuple

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    util = None


class RelevanceRanker:
    """
    Semantic and keyword-based relevance ranker for context selection.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if SENTENCE_TRANSFORMERS_AVAILABLE and self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception:
                self._model = None
        return self._model

    def rank_items(
        self,
        query: str,
        items: List[Dict[str, Any]],
        text_key: str = "content",
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank a list of item dictionaries by relevance to query.

        Args:
            query: User task or query string
            items: List of item dictionaries (e.g. memory items, symbols)
            text_key: Dictionary key containing text content to score
            top_k: Optional maximum number of items to return

        Returns:
            List of item dicts augmented with 'relevance_score', sorted in descending order
        """
        if not items:
            return []

        model = self._get_model()

        if model is not None:
            ranked = self._rank_with_transformer(query, items, text_key)
        else:
            ranked = self._rank_with_keyword_fallback(query, items, text_key)

        if top_k is not None:
            return ranked[:top_k]
        return ranked

    def _rank_with_transformer(
        self,
        query: str,
        items: List[Dict[str, Any]],
        text_key: str
    ) -> List[Dict[str, Any]]:
        """Rank using sentence-transformers cosine similarity"""
        texts = [item.get(text_key, "") for item in items]
        
        query_emb = self._model.encode(query, convert_to_tensor=True)
        doc_embs = self._model.encode(texts, convert_to_tensor=True)

        scores = util.cos_sim(query_emb, doc_embs)[0].tolist()

        ranked_items = []
        for item, score in zip(items, scores):
            item_copy = dict(item)
            item_copy["relevance_score"] = float(score)
            ranked_items.append(item_copy)

        ranked_items.sort(key=lambda x: x["relevance_score"], reverse=True)
        return ranked_items

    def _rank_with_keyword_fallback(
        self,
        query: str,
        items: List[Dict[str, Any]],
        text_key: str
    ) -> List[Dict[str, Any]]:
        """Rank using TF-IDF / term frequency fallback matching"""
        query_terms = set(query.lower().split())
        if not query_terms:
            for item in items:
                item["relevance_score"] = 0.5
            return items

        ranked_items = []
        for item in items:
            text = str(item.get(text_key, "")).lower()
            words = text.split()

            if not words:
                score = 0.0
            else:
                matches = sum(1 for term in query_terms if term in text)
                overlap_ratio = matches / len(query_terms)
                score = min(1.0, overlap_ratio)

            item_copy = dict(item)
            item_copy["relevance_score"] = round(score, 4)
            ranked_items.append(item_copy)

        ranked_items.sort(key=lambda x: x["relevance_score"], reverse=True)
        return ranked_items


def rank_context_items(
    query: str,
    items: List[Dict[str, Any]],
    text_key: str = "content"
) -> List[Dict[str, Any]]:
    """
    Convenience function to rank items by relevance.
    """
    ranker = RelevanceRanker()
    return ranker.rank_items(query, items, text_key=text_key)

"""
LangChain Anthropic Wrapper.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import Optional
from backend.core.adapters.langchain_adapter import LangChainAdapter


class AnthropicAdapter(LangChainAdapter):
    """LangChain-backed model adapter for Anthropic models."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        super().__init__(model_name=model_name, api_key=api_key)

"""
LangChain OpenAI Wrapper.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import Optional
from backend.core.adapters.langchain_adapter import LangChainAdapter


class OpenAIAdapter(LangChainAdapter):
    """LangChain-backed model adapter for OpenAI models."""

    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None):
        super().__init__(model_name=model_name, api_key=api_key)

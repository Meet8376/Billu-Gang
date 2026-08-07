"""
Pluggable Model Adapter Layer Package (LangChain & LangGraph Powered).
Member 2 — Backend Core & Model Adapter Lead
"""

from backend.core.adapters.base import ModelAdapter, CompletionResponse, ToolCallData
from backend.core.adapters.langchain_adapter import LangChainAdapter
from backend.core.adapters.langgraph_adapter import LangGraphAdapter
from backend.core.adapters.anthropic_adapter import AnthropicAdapter
from backend.core.adapters.openai_adapter import OpenAIAdapter
from backend.core.adapters.gemini_adapter import GeminiAdapter
from backend.core.adapters.gemini_langgraph_adapter import GeminiLangGraphAdapter
from backend.core.adapters.mock_adapter import MockAdapter
from backend.core.adapters.fallback_manager import FallbackAdapterManager

__all__ = [
    "ModelAdapter",
    "CompletionResponse",
    "ToolCallData",
    "LangChainAdapter",
    "LangGraphAdapter",
    "AnthropicAdapter",
    "OpenAIAdapter",
    "GeminiAdapter",
    "GeminiLangGraphAdapter",
    "MockAdapter",
    "FallbackAdapterManager",
]


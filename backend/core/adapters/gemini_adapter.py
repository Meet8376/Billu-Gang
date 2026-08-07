"""
LangChain Gemini Wrapper.
Member 2 — Backend Core & Model Adapter Lead
"""

import os
import logging
from typing import Optional, Any
from backend.core.adapters.langchain_adapter import LangChainAdapter
from backend.core.config import settings

logger = logging.getLogger(__name__)


def map_gemini_model_name(model_name: str) -> str:
    """Maps CLI model aliases to valid Google Gemini API endpoints."""
    if not model_name:
        return "gemini-2.5-flash"
    m = model_name.lower().strip()
    if "flash-lite" in m or "3.5-flash-lite" in m or "2.5-flash-lite" in m or "lite" in m:
        return "gemini-2.5-flash"
    if "1.5-pro" in m or "pro" in m:
        return "gemini-1.5-pro"
    if "1.5-flash" in m:
        return "gemini-1.5-flash"
    if "2.0-flash" in m:
        return "gemini-2.0-flash"
    if "2.5-flash" in m or "3.5" in m:
        return "gemini-2.5-flash"
    return model_name


class GeminiAdapter(LangChainAdapter):
    """LangChain-backed model adapter for Google Gemini models."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
        chat_model: Optional[Any] = None,
    ):
        target_model = map_gemini_model_name(model_name)
        resolved_key = (
            api_key
            or getattr(settings, "GEMINI_API_KEY", None)
            or getattr(settings, "GOOGLE_API_KEY", None)
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

        if resolved_key:
            os.environ["GEMINI_API_KEY"] = resolved_key
            os.environ["GOOGLE_API_KEY"] = resolved_key

        # If a pre-constructed chat_model is passed, use it directly
        if chat_model is not None:
            active_chat_model = chat_model
        else:
            active_chat_model = None
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                if resolved_key:
                    active_chat_model = ChatGoogleGenerativeAI(
                        model=target_model,
                        google_api_key=resolved_key,
                        temperature=0.2,
                    )
                else:
                    active_chat_model = ChatGoogleGenerativeAI(
                        model=target_model,
                        temperature=0.2,
                    )
            except Exception as e:
                logger.warning(f"[GeminiAdapter] Failed to initialize ChatGoogleGenerativeAI: {e}")
                active_chat_model = None

        super().__init__(
            model_name=target_model,
            api_key=resolved_key,
            chat_model=active_chat_model,
        )


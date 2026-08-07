"""
LangChain Gemini Wrapper.
Member 2 — Backend Core & Model Adapter Lead
"""

import os
from typing import Optional, Any
from backend.core.adapters.langchain_adapter import LangChainAdapter
from backend.core.config import settings


class GeminiAdapter(LangChainAdapter):
    """LangChain-backed model adapter for Google Gemini models."""

    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        api_key: Optional[str] = None,
        chat_model: Optional[Any] = None,
    ):
        resolved_key = (
            api_key
            or getattr(settings, "GEMINI_API_KEY", None)
            or getattr(settings, "GOOGLE_API_KEY", None)
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

        # If a pre-constructed chat_model is passed, use it directly
        if chat_model is not None:
            active_chat_model = chat_model
        else:
            active_chat_model = None
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                if resolved_key:
                    active_chat_model = ChatGoogleGenerativeAI(
                        model=model_name,
                        google_api_key=resolved_key,
                        temperature=0.2,
                    )
                else:
                    # Attempt standard SDK initialization (e.g. ADC / default environment)
                    active_chat_model = ChatGoogleGenerativeAI(
                        model=model_name,
                        temperature=0.2,
                    )
            except Exception:
                # Fallback to stub/mock behavior handled by parent LangChainAdapter when chat_model is None
                active_chat_model = None

        super().__init__(
            model_name=model_name,
            api_key=resolved_key,
            chat_model=active_chat_model,
        )

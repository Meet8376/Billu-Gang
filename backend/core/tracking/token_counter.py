"""
Tiktoken Token Calculator Engine.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import List, Dict, Any, Union


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Calculate exact token count for input/output text using tiktoken or fallback estimation."""
    if not text:
        return 0
    try:
        import tiktoken
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback estimation if tiktoken is unavailable or raises
        return max(1, len(text) // 4)


def count_tokens_for_messages(messages: List[Dict[str, Any]], model: str = "gpt-4o") -> int:
    """Calculate token count for a full list of OpenAI/LangChain formatted messages."""
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # message overhead: role, name, content bounds
        for key, value in message.items():
            num_tokens += count_tokens(str(value), model=model)
    num_tokens += 3  # reply primer overhead
    return num_tokens

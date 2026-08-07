"""
Tiktoken Token Calculator Engine.
Member 2 — Backend Core & Model Adapter Lead
"""

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Calculate exact token count for input/output prompts using tiktoken or fallback estimation."""
    if not text:
        return 0
    try:
        import tiktoken
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except ImportError:
        # Fallback estimation if tiktoken is not installed yet
        return max(1, len(text) // 4)

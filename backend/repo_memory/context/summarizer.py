"""
File Summarizer (FR15)

Hierarchical file summarizer for condensing oversized source code files
into compact structural outlines (classes, function signatures, imports, docstrings).
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from ..indexer.ast_parser import parse_file


class FileSummarizer:
    """
    Summarizes source code files into structural skeletons when context limits are tight.
    """

    def __init__(self, max_summary_tokens: int = 500):
        self.max_summary_tokens = max_summary_tokens

    def summarize(self, file_path: str) -> str:
        """
        Generate a compact structural summary of a source file.

        Args:
            file_path: Path to the source file

        Returns:
            Formatted structural summary string
        """
        path = Path(file_path)
        if not path.exists():
            return f"# Summary: File {file_path} not found"

        # Try parsing symbols using AST parser
        symbols = parse_file(str(path))

        lines = [
            f"# File Outline: {path.name}",
            f"# Path: {file_path}",
            f"# Extracted Symbols ({len(symbols)} total):"
        ]

        classes = [s for s in symbols if s.symbol_type == "class"]
        functions = [s for s in symbols if s.symbol_type == "function"]
        methods = [s for s in symbols if s.symbol_type == "method"]

        if classes:
            lines.append("\n## Classes:")
            for cls in classes:
                sig = cls.signature if cls.signature else f"class {cls.name}"
                lines.append(f"  - {sig} (Lines {cls.start_line}-{cls.end_line})")

        if functions:
            lines.append("\n## Top-Level Functions:")
            for fn in functions:
                sig = fn.signature if fn.signature else f"def {fn.name}(...)"
                lines.append(f"  - {sig} (Lines {fn.start_line}-{fn.end_line})")

        if methods:
            lines.append("\n## Methods:")
            for m in methods:
                parent = f"{m.parent_symbol}." if m.parent_symbol else ""
                lines.append(f"  - {parent}{m.name} (Lines {m.start_line}-{m.end_line})")

        if not symbols:
            # Fallback for plain text or unsupported formats: top 20 lines
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                head = [line.rstrip() for line in f.readlines()[:20]]
            lines.append("\n## Preview (Top 20 lines):")
            lines.extend(head)

        return "\n".join(lines)


def summarize_file(file_path: str, max_summary_tokens: int = 500) -> str:
    """
    Convenience function to summarize a file.

    Args:
        file_path: Target file path
        max_summary_tokens: Maximum summary token limit

    Returns:
        Formatted summary
    """
    summarizer = FileSummarizer(max_summary_tokens=max_summary_tokens)
    return summarizer.summarize(file_path)

#!/usr/bin/env python3

from typing import Any


def count_completed(todos: list[dict[str, Any]]) -> int:
    total = 0
    for todo in todos:
        if todo.get("done"):
            total += 1
    return total

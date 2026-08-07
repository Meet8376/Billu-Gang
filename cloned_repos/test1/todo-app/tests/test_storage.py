#!/usr/bin/env python3

from todo_app.utils import count_completed


def test_count() -> None:
    todos = [
        {"done": True},
        {"done": False},
        {"done": True},
    ]
    assert count_completed(todos) == 2

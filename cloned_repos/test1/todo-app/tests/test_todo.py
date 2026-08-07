#!/usr/bin/env python3

from todo_app.todo import TodoManager


def test_add() -> None:
    manager = TodoManager()
    manager.add("Buy Milk")
    assert len(manager.todos) == 1


def test_complete() -> None:
    manager = TodoManager()
    manager.add("Buy Milk")
    manager.complete("Buy Milk")
    assert manager.todos[0]["done"]

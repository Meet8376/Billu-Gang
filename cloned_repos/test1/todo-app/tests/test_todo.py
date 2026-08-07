#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from todo import TodoManager


def test_add():
    manager = TodoManager()
    manager.todos = []
    manager.add("Buy Milk")
    assert len(manager.todos) == 1


def test_complete():
    manager = TodoManager()
    manager.todos = []
    manager.add("Buy Milk")
    manager.complete("Buy Milk")
    assert manager.todos[0]["done"]

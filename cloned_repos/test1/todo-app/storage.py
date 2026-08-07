#!/usr/bin/env python3

import json
from typing import Any


class Storage:
    FILE = "todo-app/data/todos.json"

    def load(self) -> list[dict[str, Any]]:
        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self, todos: list[dict[str, Any]]) -> None:
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(todos, f)

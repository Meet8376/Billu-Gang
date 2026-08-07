#!/usr/bin/env python3

from typing import Any

from todo_app.storage import Storage


class TodoManager:
    def __init__(self) -> None:
        self.storage = Storage()
        self.todos: list[dict[str, Any]] = self.storage.load()

    def add(self, title: str) -> None:
        self.todos.append({"title": title, "done": False})
        self.storage.save(self.todos)

    def complete(self, title: str) -> None:
        for todo in self.todos:
            if todo["title"] == title:
                todo["done"] = True
                self.storage.save(self.todos)
                break

    def list_all(self) -> None:
        for todo in self.todos:
            print(todo)

    def search(self, keyword: str) -> list[dict[str, Any]]:
        return [t for t in self.todos if keyword in t.get("title", "")]

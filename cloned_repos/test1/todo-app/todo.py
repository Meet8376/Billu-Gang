#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from storage import Storage


class TodoManager:
    def __init__(self):
        self.storage = Storage()
        self.todos = self.storage.load()

    def add(self, title):
        self.todos.append({"title": title, "done": False})
        self.storage.save(self.todos)

    def complete(self, title):
        for todo in self.todos:
            if todo["title"] == title:
                todo["done"] = True
        self.storage.save(self.todos)

    def list_all(self):
        for todo in self.todos:
            print(todo)

    def search(self, keyword):
        return [t for t in self.todos if keyword in t["title"]]

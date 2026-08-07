#!/usr/bin/env python3

import json
import os


class Storage:
    FILE = os.path.join(os.path.dirname(__file__), "data", "todos.json")

    def load(self):
        try:
            with open(self.FILE, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self, todos):
        os.makedirs(os.path.dirname(self.FILE), exist_ok=True)
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(todos, f)

#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import count_completed


def test_count():
    todos = [
        {"done": True},
        {"done": False},
        {"done": True},
    ]
    assert count_completed(todos) == 2

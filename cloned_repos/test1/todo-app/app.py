#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from todo import TodoManager


def main():
    manager = TodoManager()

    while True:
        print("\n1. Add\n2. Complete\n3. List\n4. Search\n5. Exit")
        choice = input("> ")
        if choice == "1":
            manager.add(input("Todo: "))
        elif choice == "2":
            manager.complete(input("Complete: "))
        elif choice == "3":
            manager.list_all()
        elif choice == "4":
            print(manager.search(input("Search: ")))
        elif choice == "5":
            break


if __name__ == "__main__":
    main()

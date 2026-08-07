# Todo Application

A simple command-line Todo application written in Python with persistent JSON storage.

## Working of the Code

- **`todo-app/app.py`**: The entry point of the application. It provides an interactive command-line menu to add, complete, list, and search for todos.
- **`todo-app/todo.py`**: Contains the `TodoManager` class which handles business logic such as adding new todos, marking them as completed, listing them, and searching.
- **`todo-app/storage.py`**: Handles loading and saving todos to a JSON data file (`todo-app/data/todos.json`).
- **`todo-app/utils.py`**: Provides utility functions such as counting completed tasks.
- **`todo-app/tests/`**: Contains unit tests for testing storage, utilities, and todo management functions using `pytest`.

"""State Graph Checkpoint and Resume Manager (Member 4 Lead).

Saves state graph snapshots to disk for session resumption or cold-start benchmark replays.
"""

import json
import logging
import os
from typing import Optional
from backend.orchestrator.graph.task_planner import TaskGraphState

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manages disk serialization and restoration of TaskGraphState."""

    @staticmethod
    def save_checkpoint(state: TaskGraphState, filepath: str) -> str:
        """Serializes current TaskGraphState to JSON file on disk."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        json_data = state.model_dump_json(indent=2)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_data)
        logger.info(f"Saved TaskGraphState checkpoint for session '{state.session_id}' to {filepath}")
        return filepath

    @staticmethod
    def load_checkpoint(filepath: str) -> TaskGraphState:
        """Deserializes TaskGraphState from JSON file on disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Checkpoint file not found at: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = f.read()

        state = TaskGraphState.model_validate_json(raw_data)
        logger.info(f"Restored TaskGraphState checkpoint for session '{state.session_id}' from {filepath}")
        return state


def save_checkpoint(state: TaskGraphState, filepath: str) -> str:
    """Helper utility for state graph checkpoint saving."""
    return CheckpointManager.save_checkpoint(state, filepath)


def load_checkpoint(filepath: str) -> TaskGraphState:
    """Helper utility for state graph checkpoint loading."""
    return CheckpointManager.load_checkpoint(filepath)

"""Unit tests for State Graph Checkpoints and Cold-Start Replays (Member 4 Lead)."""

import os
import tempfile
from backend.orchestrator.graph.checkpoints import CheckpointManager, load_checkpoint, save_checkpoint
from backend.orchestrator.graph.task_planner import TaskPlanner, TaskStatus


def test_checkpoint_save_and_load():
    """Verify serialization and restoration of TaskGraphState."""
    initial_state = TaskPlanner.create_initial_plan("sess-chk-1", "Fix race condition in background worker")

    # Modify status on a node
    node_id = list(initial_state.nodes.keys())[0]
    initial_state.nodes[node_id].status = TaskStatus.SUCCESS

    with tempfile.TemporaryDirectory() as tmp_dir:
        chk_path = os.path.join(tmp_dir, "checkpoint_test.json")

        # Save checkpoint
        saved_file = save_checkpoint(initial_state, chk_path)
        assert os.path.exists(saved_file)

        # Load checkpoint
        restored_state = load_checkpoint(chk_path)

        assert restored_state.session_id == initial_state.session_id
        assert restored_state.issue_description == initial_state.issue_description
        assert len(restored_state.nodes) == len(initial_state.nodes)
        assert restored_state.nodes[node_id].status == TaskStatus.SUCCESS

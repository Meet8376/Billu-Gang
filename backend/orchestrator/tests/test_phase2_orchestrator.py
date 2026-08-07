"""Unit tests for Member 4 Phase 2 Orchestrator & Sandbox components."""

import asyncio
from backend.orchestrator.graph.task_planner import TaskPlanner, TaskStatus, TaskType
from backend.orchestrator.graph.state_graph import TaskGraphOrchestrator
from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig
from backend.orchestrator.sandbox.container_exec import ContainerExecService
from backend.orchestrator.sandbox.snapshot_manager import SnapshotManager
from backend.orchestrator.security.approval_gate import ApprovalGate


def test_task_planner_dag_creation():
    """Verify initial DAG generation and dependency chaining."""
    state = TaskPlanner.create_initial_plan("session-123", "Fix overflow bug in paginator")
    assert len(state.nodes) == 5
    assert state.active_node_id is not None

    # Check executable nodes (should be Node 1: Reproduce)
    exec_nodes = TaskPlanner.get_executable_nodes(state)
    assert len(exec_nodes) == 1
    assert exec_nodes[0].task_type == TaskType.REPRODUCE


def test_task_graph_orchestrator_execution():
    """Verify TaskGraphOrchestrator state transitions and event emitting."""
    orchestrator = TaskGraphOrchestrator("sess-456", ".", "Fix edge case bug")
    events = []

    async def mock_listener(evt_type, data):
        events.append(evt_type)

    orchestrator.subscribe(mock_listener)
    snapshot = orchestrator.get_graph_snapshot()
    assert snapshot["session_id"] == "sess-456"
    assert len(snapshot["nodes"]) == 5

    # Mock handler
    async def mock_handler(node):
        return {"output": f"Completed {node.title}"}

    # Execute step
    node_res = asyncio.run(orchestrator.execute_node_step(mock_handler))
    assert node_res is not None
    assert node_res.status == TaskStatus.SUCCESS
    assert "node_started" in events
    assert "node_completed" in events


def test_container_exec_service():
    """Verify ContainerExecService command safety check and execution."""
    config = SandboxConfig(host_workspace_path=".")
    sandbox = DockerSandbox(config)
    sandbox.start()

    exec_service = ContainerExecService(sandbox)
    res = asyncio.run(exec_service.execute_command("pytest tests/"))

    assert res.approved is True
    assert res.exit_code == 0
    assert "pytest" in res.stdout
    sandbox.destroy()


def test_snapshot_manager():
    """Verify SnapshotManager checkpoint creation and rollback."""
    config = SandboxConfig(host_workspace_path=".")
    sandbox = DockerSandbox(config)
    sandbox.start()

    snap_mgr = SnapshotManager(sandbox)
    snap_mgr.initialize_workspace_git()

    # Create checkpoint
    snap1 = snap_mgr.create_checkpoint("step1", "Baseline checkpoint")
    assert snap1.snapshot_id.startswith("snap-")
    assert len(snap_mgr.list_snapshots()) == 1

    # Rollback
    rolled_back = snap_mgr.rollback_to_snapshot(snap1.snapshot_id)
    assert rolled_back is True
    sandbox.destroy()

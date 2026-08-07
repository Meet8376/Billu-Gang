"""Master Integration Test Runner for Member 4 Task Orchestrator & Sandbox Security.

Executes test suites across all 6 Phases (Phases 1 through 6).
"""

import os
import sys

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.orchestrator.tests.test_docker_sandbox import test_approval_gate_policy, test_emergency_stop_manager, test_sandbox_config_defaults, test_sandbox_lifecycle_mock
from backend.orchestrator.tests.test_phase2_orchestrator import test_container_exec_service, test_snapshot_manager, test_task_graph_orchestrator_execution, test_task_planner_dag_creation
from backend.orchestrator.tests.test_phase3_orchestrator import test_agent_nodes_execution, test_network_policy_enforcer, test_secret_redactor
from backend.orchestrator.tests.test_replanning import test_replanning_on_verification_failure
from backend.orchestrator.tests.test_emergency_stop import test_emergency_stop_manager_singleton_and_pause
from backend.orchestrator.tests.test_network_policy import test_network_policy_default_deny_and_allowlist
from backend.orchestrator.tests.test_parallel_executor import test_parallel_sub_agent_execution
from backend.orchestrator.tests.test_checkpoints import test_checkpoint_save_and_load
from backend.orchestrator.tests.test_load_isolation import test_sandbox_lifecycle_load_and_cleanup
from backend.orchestrator.tests.test_phase6_quickstart import test_quickstart_validation_routines


def run_all_member_4_tests() -> bool:
    """Executes test suites across Phases 1 through 6."""
    print("=" * 70)
    print("      AE-01 Member 4 Orchestrator & Sandbox Complete Test Suite")
    print("=" * 70)

    test_cases = [
        # Phase 1: Sandboxed Infrastructure & Security
        ("Phase 1: Sandbox Config Defaults", test_sandbox_config_defaults),
        ("Phase 1: Sandbox Lifecycle Mock", test_sandbox_lifecycle_mock),
        ("Phase 1: Emergency Stop Manager", test_emergency_stop_manager),
        ("Phase 1: Approval Gate Security Policy", test_approval_gate_policy),

        # Phase 2: Task Orchestration & Graph Engine
        ("Phase 2: Task Planner DAG Creation", test_task_planner_dag_creation),
        ("Phase 2: Task Graph Orchestrator Execution", test_task_graph_orchestrator_execution),
        ("Phase 2: Container Exec Service", test_container_exec_service),
        ("Phase 2: Snapshot Manager Checkpoints", test_snapshot_manager),

        # Phase 3: Connected Orchestrator, Secret Redaction & Isolation
        ("Phase 3: Secret Redactor & Scrubber", test_secret_redactor),
        ("Phase 3: Network Policy Enforcer", test_network_policy_enforcer),
        ("Phase 3: Specialist Agent Nodes Execution", test_agent_nodes_execution),

        # Phase 4: Dynamic Replanning & Interrupt Handlers
        ("Phase 4: Replanning Engine Self-Healing", test_replanning_on_verification_failure),
        ("Phase 4: Emergency Stop & /pause Interrupt", test_emergency_stop_manager_singleton_and_pause),
        ("Phase 4: Default-Deny Network Isolation", test_network_policy_default_deny_and_allowlist),

        # Phase 5: Parallel Sub-Agents, Checkpoints & Load Isolation
        ("Phase 5: Parallel Sub-Agent Execution (FR19)", test_parallel_sub_agent_execution),
        ("Phase 5: State Graph Checkpoints & Replay", test_checkpoint_save_and_load),
        ("Phase 5: Sandbox Lifecycle Load & Isolation", test_sandbox_lifecycle_load_and_cleanup),

        # Phase 6: Quick-Start Setup & Validation
        ("Phase 6: Quick-Start Setup Validation", test_quickstart_validation_routines),
    ]

    passed_count = 0
    failed_count = 0

    for name, test_fn in test_cases:
        try:
            print(f"Running [{name}]...", end=" ")
            test_fn()
            print("[OK] PASSED")
            passed_count += 1
        except Exception as e:
            print(f"[FAIL] FAILED: {e}")
            failed_count += 1

    print("=" * 70)
    print(f"RESULTS: {passed_count} Passed | {failed_count} Failed | Total: {len(test_cases)}")
    print("=" * 70)

    if failed_count == 0:
        print("ALL MEMBER 4 PHASES 1 THROUGH 6 TESTS PASSED 100%!")
        return True
    else:
        print("Some tests failed. Please review errors above.")
        return False


if __name__ == "__main__":
    success = run_all_member_4_tests()
    sys.exit(0 if success else 1)

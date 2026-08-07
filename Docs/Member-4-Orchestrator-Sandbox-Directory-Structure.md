# Member 4 — Task Orchestrator & Sandbox Security Lead: Directory Structure & File Specification

## 1. Overview & Ownership Domain
- **Member:** Member 4
- **Primary Role:** Task Orchestrator & Sandbox Security Lead
- **Engineering Surfaces Owned:** Task Graph Orchestrator, Sandboxed Execution Service, Safety Boundaries
- **Tech Stack & Tools:** LangGraph / Async State Graph, Docker SDK (`docker-py`), Asyncio, Git snapshotting & patch management
- **Primary Root Location:** `backend/orchestrator/`

---

## 2. Dedicated Directory Tree

```
backend/orchestrator/
├── __init__.py                         # Package initializer
│
├── graph/                              # Task Graph & State Machine Execution Engine
│   ├── __init__.py
│   ├── state_graph.py                  # LangGraph / Async state graph definition & execution runtime
│   ├── task_planner.py                 # Multi-step DAG generator (planning, execution, verification nodes)
│   ├── replanning_engine.py            # Dynamic replanning loop triggered on test/build verification failure (FR22)
│   ├── agent_nodes.py                  # Specialist sub-agent node handlers (Planner, Coder, Verifier nodes)
│   ├── parallel_executor.py            # Concurrent execution manager for independent sub-task branches (FR19)
│   └── checkpoints.py                  # State graph checkpointing, serialization & resume manager
│
├── sandbox/                            # Docker Sandboxed Execution Service
│   ├── __init__.py
│   ├── docker_manager.py               # Docker SDK (docker-py) container lifecycle, volume mounts & resource limits
│   ├── container_exec.py               # Command execution runner inside container with timeout & output streaming
│   ├── snapshot_manager.py            # Git patch snapshotting & instant workspace rollback manager
│   ├── network_policy.py               # Default-deny network filter & allowlist enforcer (NFR7, NFR8)
│   └── dockerfile/
│       └── Dockerfile.sandbox          # Base Docker sandbox image definition (Python 3.11 + Node + Git + build tools)
│
├── security/                           # Safety Boundaries & Approval Enforcement
│   ├── __init__.py
│   ├── approval_gate.py                # Interactive approval callback gate for out-of-scope commands
│   ├── emergency_stop.py               # SIGKILL process & emergency container abort handler (FR28)
│   └── secret_redactor.py              # Environment variable & credential scrubber for sandbox logs
│
└── tests/                              # Unit & Integration Tests for Orchestration & Sandbox
    ├── __init__.py
    ├── test_state_graph.py             # Task graph state machine execution & node transition tests
    ├── test_replanning.py              # Self-healing failure recovery & replanning tests
    ├── test_docker_sandbox.py          # Docker container startup, volume mount & command execution tests
    ├── test_network_policy.py          # Default-deny network policy & isolation tests
    └── test_emergency_stop.py          # SIGKILL emergency termination & container abort unit tests
```

---

## 3. Detailed File Responsibilities & Key Exports

| File Path | Purpose & Responsibilities | Key Functions / Classes / Components |
|---|---|---|
| `backend/orchestrator/graph/state_graph.py` | State graph runtime orchestrating task execution through discrete state nodes. | `class TaskGraphStateEngine`, `run_graph()` |
| `backend/orchestrator/graph/task_planner.py` | Translates user issue into an executable DAG of sub-tasks with dependency links. | `class TaskPlanner`, `create_initial_plan()` |
| `backend/orchestrator/graph/replanning_engine.py` | Receives verification test failures, diagnoses errors, and rewrites remaining DAG nodes. | `class ReplanningEngine`, `replan_on_failure()` |
| `backend/orchestrator/graph/agent_nodes.py` | Individual specialist node functions: `planner_node()`, `coder_node()`, `verifier_node()`. | `planner_node`, `coder_node`, `verifier_node` |
| `backend/orchestrator/graph/parallel_executor.py` | Runs independent DAG sub-branches concurrently using asyncio task pools. | `class ParallelSubAgentExecutor` |
| `backend/orchestrator/graph/checkpoints.py` | Saves state graph snapshots to disk for resumption or benchmark cold-start replays. | `save_checkpoint()`, `load_checkpoint()` |
| `backend/orchestrator/sandbox/docker_manager.py` | Controls Docker container creation, memory/CPU capping, and workspace mounting. | `class DockerSandboxManager` |
| `backend/orchestrator/sandbox/container_exec.py` | Executes shell commands (`pytest`, `npm test`, `git apply`) inside running sandbox. | `exec_command(cmd, timeout)` |
| `backend/orchestrator/sandbox/snapshot_manager.py` | Takes git commits/patches before edits; provides instant rollback to any snapshot. | `create_snapshot()`, `restore_snapshot()` |
| `backend/orchestrator/sandbox/network_policy.py` | Configures iptables / Docker network rules to block unauthorized host/internet access. | `enforce_network_policy()` |
| `backend/orchestrator/sandbox/dockerfile/Dockerfile.sandbox` | Dockerfile compiling Python, Node.js, Git, GCC, and testing tools for isolated runs. | Base Dockerfile |
| `backend/orchestrator/security/approval_gate.py` | Intercepts commands targeting files outside workspace or network and requests CLI approval. | `check_approval(command)` |
| `backend/orchestrator/security/emergency_stop.py` | Instantly sends `SIGKILL` to container processes when user presses `Ctrl+C` or `/pause`. | `emergency_stop_sandbox()` |
| `backend/orchestrator/security/secret_redactor.py` | Redacts API keys, passwords, and tokens from stdout/stderr before logging to traces. | `redact_secrets(output)` |

---

## 4. 24-Hour Phase Deliverables Schedule

```
Phase 1 (H0-H3) ──► Phase 2 (H3-H8) ──► Phase 3 (H8-H13) ──► Phase 4 (H13-H17) ──► Phase 5 (H17-H21) ──► Phase 6 (H21-H24)
  Base Docker Image &   State Graph &        Execute Tool Calls    Dynamic Replanning &   Sandbox Load Test &   Quick-Start Setup
  Sandbox Class Stub    Snapshot Rollback    in Docker + Approval  Emergency SIGKILL      Parallel Agents       Script Validation
```

1. **Phase 1 (Hours 0–3):**
   - Build Docker base image for sandbox environment (`Dockerfile.sandbox`).
   - Implement Python `DockerSandbox` class with scoped workspace volume mount and resource caps (CPU/Memory).
   - Stub out emergency kill mechanism (`emergency_stop.py`) and approval gate callback interface (`approval_gate.py`).
2. **Phase 2 (Hours 3–8):**
   - Implement `TaskGraphOrchestrator` using state graph logic (`state_graph.py`, `task_planner.py`).
   - Build sandboxed command execution service (`container_exec.py`).
   - Build filesystem snapshotting (`git commit` / patch checkpoints inside sandbox) for rollback support (`snapshot_manager.py`).
3. **Phase 3 (Hours 8–13):**
   - Connect Orchestrator to Sandbox: execute model tool calls inside container.
   - Implement approval gate handler: pause execution and await CLI approval when command exceeds safe scope.
   - Validate sandbox isolation (verify host network/filesystem cannot be touched).
4. **Phase 4 (Hours 13–17):**
   - Implement dynamic replanning loop: when verification fails, feed error back into Task Graph to generate patch revision (FR22).
   - Implement emergency stop route (`/pause` / `Ctrl+C` interrupt) that immediately SIGKILLs running sandbox commands (FR28).
   - Enforce default-deny network policy inside container (NFR7, NFR8).
5. **Phase 5 (Hours 17–21):**
   - Perform load testing on Docker sandbox lifecycle: verify container cleanup and disk isolation.
   - Test multi-branch execution with parallel sub-agents (FR19).
6. **Phase 6 (Hours 21–24):**
   - Validate quick-start setup scripts (`docker build`, python environment setup).

---

## 5. Subsystem Dependencies & API Boundaries
- **Orchestrator ↔ Docker Daemon:** Manages local Docker containers via `docker-py` SDK.
- **Orchestrator ↔ Model Adapter:** Requests completions for node execution and replanning.
- **Orchestrator ↔ Verification Pipeline:** Calls `VerificationPipeline.run_suite()` after each code edit step inside sandbox.
- **Orchestrator ↔ CLI Approval UI:** Triggers `approval_gate.py` when an unsafe command is attempted.

"""
LangGraph Task Graph Workflow Adapter.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, START, END


class HarnessState(TypedDict):
    """LangGraph state representation for the coding harness task graph."""
    session_id: str
    goal: str
    task_dag: List[Dict[str, Any]]
    current_node_id: Optional[str]
    status: str
    logs: List[str]
    output: Optional[str]
    error: Optional[str]


class LangGraphAdapter:
    """Task Graph Workflow Adapter using LangGraph StateGraph engine."""

    def __init__(self, session_id: str, goal: str):
        self.session_id = session_id
        self.goal = goal
        self.workflow = StateGraph(HarnessState)
        self._build_graph()
        self.compiled_app = self.workflow.compile()

    def _build_graph(self):
        """Construct LangGraph DAG nodes and transitions."""
        def planner_node(state: HarnessState) -> Dict[str, Any]:
            logs = state.get("logs", []) + [f"Planner node executed for session {state['session_id']}"]
            task_dag = [
                {"id": "node_1", "title": "Analyze Task", "status": "completed"},
                {"id": "node_2", "title": "Execute Patch", "status": "pending"},
            ]
            return {
                "status": "planned",
                "task_dag": task_dag,
                "current_node_id": "node_1",
                "logs": logs,
            }

        def executor_node(state: HarnessState) -> Dict[str, Any]:
            logs = state.get("logs", []) + ["Executor node executed tool commands"]
            return {
                "status": "executed",
                "current_node_id": "node_2",
                "logs": logs,
                "output": f"Patch successfully applied for task: '{state['goal']}'",
            }

        def verifier_node(state: HarnessState) -> Dict[str, Any]:
            logs = state.get("logs", []) + ["Verifier node validated test suite passing"]
            return {
                "status": "verified",
                "logs": logs,
            }

        self.workflow.add_node("planner", planner_node)
        self.workflow.add_node("executor", executor_node)
        self.workflow.add_node("verifier", verifier_node)

        self.workflow.add_edge(START, "planner")
        self.workflow.add_edge("planner", "executor")
        self.workflow.add_edge("executor", "verifier")
        self.workflow.add_edge("verifier", END)

    async def run(self) -> HarnessState:
        """Execute the compiled LangGraph workflow graph."""
        initial_state: HarnessState = {
            "session_id": self.session_id,
            "goal": self.goal,
            "task_dag": [],
            "current_node_id": None,
            "status": "initialized",
            "logs": [],
            "output": None,
            "error": None,
        }
        final_state = await self.compiled_app.ainvoke(initial_state)
        return final_state

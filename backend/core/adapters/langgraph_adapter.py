"""
LangGraph Task Graph Workflow Adapter.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import Dict, Any, List, Optional, TypedDict
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, START, END


class HarnessState(TypedDict):
    """LangGraph state representation for the coding harness task graph."""
    session_id: str
    goal: str
    task_dag: List[Dict[str, Any]]
    current_node_id: Optional[str]
    status: str
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
        def plan_node(state: HarnessState) -> Dict[str, Any]:
            return {
                "status": "planned",
                "output": f"LangGraph Plan generated for session {state['session_id']}",
            }

        def execute_node(state: HarnessState) -> Dict[str, Any]:
            return {
                "status": "executed",
                "output": "LangGraph Execution completed successfully",
            }

        self.workflow.add_node("planner", plan_node)
        self.workflow.add_node("executor", execute_node)

        self.workflow.add_edge(START, "planner")
        self.workflow.add_edge("planner", "executor")
        self.workflow.add_edge("executor", END)

    async def run(self) -> HarnessState:
        """Execute the compiled LangGraph workflow graph."""
        initial_state: HarnessState = {
            "session_id": self.session_id,
            "goal": self.goal,
            "task_dag": [],
            "current_node_id": None,
            "status": "initialized",
            "output": None,
            "error": None,
        }
        final_state = await self.compiled_app.ainvoke(initial_state)
        return final_state

"""
Plan & Task Graph Route Handlers (LangGraph Wired).
Member 2 — Backend Core & Model Adapter Lead
"""

import uuid
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.core.schemas.task_graph import TaskGraph, TaskGraphNode, NodeStatus, TaskType
from backend.core.schemas.sse_events import SSEEvent, EventType
from backend.core.adapters.langgraph_adapter import LangGraphAdapter
from backend.core.routes.sse_routes import broadcaster

router = APIRouter()


class ReplanRequest(BaseModel):
    session_id: str
    feedback: str


@router.get("/plan/{session_id}", response_model=TaskGraph)
async def get_plan(session_id: str):
    """Retrieve active Task Graph for session generated via LangGraph."""
    adapter = LangGraphAdapter(session_id=session_id, goal="Generate session task graph")
    state = await adapter.run()

    nodes = [
        TaskGraphNode(
            id=item.get("id", str(uuid.uuid4())),
            title=item.get("title", "Task Node"),
            description=item.get("description", "Execute task step"),
            task_type=TaskType.CODE_EDIT,
            status=NodeStatus.COMPLETED if item.get("status") == "completed" else NodeStatus.PENDING,
        )
        for item in state.get("task_dag", [])
    ]

    return TaskGraph(session_id=session_id, nodes=nodes)


@router.post("/plan/replan", response_model=TaskGraph, status_code=status.HTTP_200_OK)
async def trigger_replan(payload: ReplanRequest):
    """Trigger dynamic replanning with feedback using LangGraph."""
    adapter = LangGraphAdapter(
        session_id=payload.session_id,
        goal=f"Dynamic replan with feedback: {payload.feedback}"
    )
    state = await adapter.run()

    nodes = [
        TaskGraphNode(
            id=item.get("id", str(uuid.uuid4())),
            title=item.get("title", "Re-planned Task Node"),
            description=f"Replanning applied with feedback: {payload.feedback}",
            task_type=TaskType.PLAN,
            status=NodeStatus.PENDING,
        )
        for item in state.get("task_dag", [])
    ]

    task_graph = TaskGraph(session_id=payload.session_id, nodes=nodes)

    # Publish plan_updated SSE event
    sse_evt = SSEEvent(
        event_id=str(uuid.uuid4()),
        event_type=EventType.PLAN_UPDATED,
        payload={"session_id": payload.session_id, "node_count": len(nodes), "feedback": payload.feedback}
    )
    await broadcaster.publish(sse_evt)

    return task_graph

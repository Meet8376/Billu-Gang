"""
Plan & Task Graph Route Handlers.
Member 2 — Backend Core & Model Adapter Lead
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.core.schemas.task_graph import TaskGraph

router = APIRouter()


class ReplanRequest(BaseModel):
    session_id: str
    feedback: str


@router.get("/plan/{session_id}", response_model=TaskGraph)
async def get_plan(session_id: str):
    """Retrieve active Task Graph for session."""
    return TaskGraph(session_id=session_id, nodes=[])


@router.post("/plan/replan", response_model=TaskGraph, status_code=status.HTTP_200_OK)
async def trigger_replan(payload: ReplanRequest):
    """Trigger dynamic replanning with feedback."""
    return TaskGraph(session_id=payload.session_id, nodes=[])

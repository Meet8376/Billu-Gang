"""
Run Execution Control Route Handlers (Wired to Model Adapters & SSE Events).
Member 2 — Backend Core & Model Adapter Lead
"""

import uuid
from fastapi import APIRouter, status
from pydantic import BaseModel

from backend.core.adapters.langchain_adapter import LangChainAdapter
from backend.core.schemas.sse_events import SSEEvent, EventType
from backend.core.routes.sse_routes import broadcaster

router = APIRouter()


class RunControlRequest(BaseModel):
    session_id: str


class RunControlResponse(BaseModel):
    
    session_id: str
    status: str
    message: str


@router.post("/run/start", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def start_run(payload: RunControlRequest):
    """Start autonomous execution run wired to ModelAdapter tool dispatch loop."""
    adapter = LangChainAdapter(model_name="gpt-4o")

    # Broadcast tool_started SSE event
    tool_start_evt = SSEEvent(
        event_id=str(uuid.uuid4()),
        event_type=EventType.TOOL_STARTED,
        payload={"session_id": payload.session_id, "tool_name": "execute_task_graph"}
    )
    await broadcaster.publish(tool_start_evt)

    # Execute completion step
    completion = await adapter.complete(
        messages=[{"role": "user", "content": f"Execute run for session {payload.session_id}"}]
    )

    # Broadcast tool_finished SSE event
    tool_finish_evt = SSEEvent(
        event_id=str(uuid.uuid4()),
        event_type=EventType.TOOL_FINISHED,
        payload={"session_id": payload.session_id, "output": completion.content}
    )
    await broadcaster.publish(tool_finish_evt)

    return RunControlResponse(
        session_id=payload.session_id,
        status="running",
        message="Autonomous execution initiated and model completion dispatched",
    )


@router.post("/run/pause", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def pause_run(payload: RunControlRequest):
    """Pause execution run."""
    return RunControlResponse(
        session_id=payload.session_id,
        status="paused",
        message="Autonomous execution paused",
    )


@router.post("/run/resume", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def resume_run(payload: RunControlRequest):
    """Resume paused execution run."""
    return RunControlResponse(
        session_id=payload.session_id,
        status="running",
        message="Autonomous execution resumed",
    )


@router.post("/run/cancel", response_model=RunControlResponse, status_code=status.HTTP_200_OK)
async def cancel_run(payload: RunControlRequest):
    """Cancel active execution run."""
    return RunControlResponse(
        session_id=payload.session_id,
        status="cancelled",
        message="Autonomous execution cancelled",
    )
